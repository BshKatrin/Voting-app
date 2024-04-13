from sqlite3 import Connection
from typing import Set, Dict

from electoral_systems import Election, VotingRulesConstants
from people import Candidate, Elector

# Pour une génération des docs uniquement
__pdoc__ = {
    'ImportData._check_tables': True,
    'ImportData._get_existing_tables': True,
    'ImportData._check_columns': True,
    'ImportData._check_columns_people': True,
    'ImportData._import_results': True,
    'ImportData._import_one_round': True,
    'ImportData._import_multi_round': True,
    'ImportData._import_condorcet': True,
    'ImportData._import_config': True,
}


class ImportData:
    """Une classe qui fournit les fonctionnalités nécessaires pour une importation des données dans l'élection.
    SQLite3 est utilisé."""

    election: Election = Election()
    IMPORT: str = "I"

    @classmethod
    def _check_tables(cls, tables_to_check: Set[str], existing_tables: Set[str]) -> tuple[bool, Set[str]]:
        """Vérifie que les tableaux dans `tables_to_check` sont présents dans la base des données qui
        contient les tableaux dans `existing_tables`.

        Args:
            tables_to_check (Set[str]): Des noms tableaux dont l'existence il faut vérifier.
            existing_tables (Set[str]): Des noms des tableaux qui existe dans la base des données.

        Returns:
            tuple[bool, Set[str]]: Un booléen `True` s'il manque au moins un tableau dans la base de données.
                Un ensemble contenant les noms des tableaux manquants. Un booléen `False` si tous les tableaux sont bien présents,
                l'ensemble est vide dans ce cas.
        """

        missing_tables = tables_to_check - (tables_to_check & existing_tables)
        return (bool(missing_tables), missing_tables)

    @classmethod
    def _get_existing_tables(cls, connection: Connection) -> Set[str]:
        """Retourne des noms des tableaux qui existent dans la base des données.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.

        Returns:
            Set[str]: Un ensemble des noms des tableaux.
        """

        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        return {row[0] for row in cursor.fetchall()}

    @classmethod
    def _check_columns(cls, connection: Connection, tables_cols: Dict[str, tuple[str, str]]) -> bool:
        """Vérifie les noms des colonnes et leur affinité de type.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            tables_cols (Dict[str, tuple[str, str]]): Un dictionnnaire dont les clés sont des noms des tableaux qui existent
                dans la base des données. Des valeurs associées sont des noms des colonnes et leur affinité de type qu'il faut vérifier.

        Returns:
            bool: `True` si chaque tableau contient des colonnes de données avec la bonne affinité de type. Sinon, `False`.
        """

        cursor = connection.cursor()
        for table, columns in tables_cols.items():
            cursor.execute(
                f"SELECT name, type FROM pragma_table_info('{table}')")
            existing_columns = {(row[0], row[1]) for row in cursor.fetchall()}
            missing_columns = columns - (columns & existing_columns)
            if missing_columns:
                return True
        return False

    @classmethod
    def _check_columns_people(cls, connection: Connection) -> bool:
        """Vérifie des colonnes et leur affinité de type pour les tableaux des candidats et des électeurs.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.

        Returns:
            bool: `True` si chaque tableau contient des colonnes de données avec la bonne affinité de type. Sinon, `False`.
        """

        return cls._check_columns(
            connection,
            {
                "candidates": {
                    ("id", "INTEGER"),
                    ("x", "REAL"),
                    ("y", "REAL"),
                    ("first_name", "TEXT"),
                    ("last_name", "TEXT"),
                    ("dogmatism", "REAL"),
                    ("opposition", "REAL"),
                },
                "electors": {
                    ("id", "INTEGER"),
                    ("x", "REAL"),
                    ("y", "REAL"),
                    ("weight", "INTEGER"),
                    ("knowledge", "REAL"),
                },
            },
        )

    @classmethod
    def import_people(cls, connection: Connection, with_results: bool) -> tuple[bool, str]:
        """Importe des données dans l'élection à partir de la base des données. Fait les vérifications
        nécessaires des tableaux et des colonnes.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            with_results (bool): `True` s'il faut importer les résultats. `False`, s'il faut importer sans les résultats.

        Returns:
            tuple[bool, str]: Un booléen `True` si les données ont été importées avec succès, `False` si l'erreur est survenue.
                Une chaîne de caractères avec le message.
        """

        if with_results:
            return cls.import_people_with_results(connection)
        return cls.import_people_no_results(connection)

    @classmethod
    def import_people_no_results(cls, connection: Connection) -> tuple[bool, str]:
        """Importe des données (candidats, électeurs uniquement) dans une élection à partir de la base des données.
        Fait les vérifications nécessaires des tableaux et des colonnes.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.

        Returns:
            tuple[bool, str]: Un booléen `True` si les données ont été importées avec succès, `False`s si l'erreur est survenue.
                Une chaîne de caractères avec le message.
        """

        existing_tables = cls._get_existing_tables(connection)
        # Check tables
        missing, missing_tables = cls._check_tables(
            {"candidates", "electors"}, existing_tables
        )
        if missing:
            return False, f"Tables {missing_tables} are not found"

        # Check columns
        missing = cls._check_columns_people(connection)

        if missing:
            return False, f"Database does not correspond"

        cursor = connection.cursor()

        cursor.execute("SELECT x, y, first_name, last_name FROM candidates")
        candidates_data = cursor.fetchall()
        max_fst_name = "A"
        max_lst_name = "A"
        for x, y, first_name, last_name in candidates_data:
            id = next(cls.election.id_iter)
            cls.election.add_candidate_import(
                Candidate(
                    id=id, position=(
                        x, y), first_name=first_name, last_name=last_name
                )
            )

        cursor.execute("SELECT x, y, weight, knowledge FROM electors")
        electors_data = cursor.fetchall()

        for x, y, weight, knowledge in electors_data:
            id = next(cls.election.id_iter)
            cls.election.add_elector_import(
                Elector(id=id, position=(x, y),
                        weight=weight, knowledge=knowledge)
            )
        return True, "Data imported"

    @classmethod
    def import_people_with_results(cls, connection: Connection) -> tuple[bool, str]:
        """Importe des données (candidats, électeurs, résultats) dans l'élection à partir de la base des données.
        Fait les vérifications nécessaires des tableaux et des colonnes. Importe les configurations de l'élection
        si le tableau correspondant est présent. Supprime toutes les données existantes de l'élection.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.

        Returns:
            tuple[bool, str]: `True` si les données ont été importées avec succès, `False` si l'erreur est survenue.
                Une chaîne de caractères avec le message.
        """

        cls.election.delete_all_data()
        cls.election.nb_polls = 0
        # Check tables
        existing_tables = cls._get_existing_tables(connection)
        missing, missing_tables = cls._check_tables(
            {"candidates", "electors"}, existing_tables
        )
        if missing:
            return False, f"Tables {missing_tables} are not found"

        # Check columns
        missing = cls._check_columns_people(connection)
        if missing:
            return False, f"Database does not correspond"

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM candidates")
        candidates_data = cursor.fetchall()

        # id : candidate
        candidates_id_assoc = dict()

        for id, x, y, first_name, last_name, dogm, oppos in candidates_data:
            new_candidate = Candidate(
                id=next(cls.election.id_iter),
                position=(x, y),
                first_name=first_name,
                last_name=last_name,
                dogmatism=dogm,
                opposition=oppos,
            )
            cls.election.add_candidate_import(new_candidate)
            candidates_id_assoc[id] = new_candidate

        cursor.execute("SELECT * FROM electors")
        electors_data = cursor.fetchall()

        for id, x, y, weight, knowledge in electors_data:
            new_elector = Elector(
                id=id,
                position=(x, y),
                weight=weight,
                knowledge=knowledge,
            )
            cls.election.add_elector_import(new_elector)

        table_missing, _ = cls._check_tables({"settings"}, existing_tables)
        cls._import_config(connection, table_missing)
        return cls._import_results(connection, existing_tables, candidates_id_assoc)

    @classmethod
    def _import_results(cls, connection: Connection, existing_tables: Set[str], assoc: Dict[int, Candidate]) -> tuple[bool, str]:
        """Importe des résultats de chaque règle de vote présente dans la base des données dans  l'élection.
        Fait les vérifications nécessaires des tableaux et des colonnes.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            existing_tables (Set[str]): Un ensemble des noms des tableaux qui existent dans la base des données.
            assoc (Dict[int, people.candidate.Candidate]): Un dictionnaire associant à chaque ID de candidat
                (ID dans la base de données) le candidat correspondant dans l'élection.
                Ceci est nécessaire en raison de la possibilité de divergence de ces IDs.

        Returns:
            tuple[bool, str]: Un booléen `True` si les données ont été importées avec succès, `False` si l'erreur est survenue.
                Une chaîne de caractères avec le message.
        """

        _, missing_tables = cls._check_tables(
            {"results_one_round", "results_multi_round", "results_condorcet"},
            existing_tables,
        )

        if len(missing_tables) == 3:
            return False, "No tables related to scores found"

        if "results_one_round" in existing_tables:
            # Check columns
            missing = cls._check_columns(
                connection,
                {
                    "results_one_round": {
                        ("candidate_id", "INTEGER"),
                        ("voting_rule", "TEXT"),
                        ("score", "REAL"),
                    },
                },
            )
            if missing:
                return False, f"Database does not correspond"

            cls._import_one_round(connection, assoc)

        if "results_multi_round" in existing_tables:
            missing = cls._check_columns(
                connection,
                {
                    "results_multi_round": {
                        ("candidate_id", "INTEGER"),
                        ("voting_rule", "TEXT"),
                        ("round", "INTEGER"),
                        ("score", "REAL"),
                    },
                },
            )
            if missing:
                return False, f"Database does not correspond"
            cls._import_multi_round(connection, assoc)

        if ("results_condorcet" in existing_tables and "condorcet_duels" in existing_tables):
            missing = cls._check_columns(
                connection,
                {
                    "results_condorcet": {
                        ("candidate_id", "INTEGER"),
                        ("voting_rule", "TEXT"),
                        ("score", "REAL"),
                    },
                    "condorcet_duels": {
                        ("winner_id", "INTEGER"),
                        ("loser_id", "INTEGER"),
                        ("score", "REAL"),
                    },
                },
            )
            if missing:
                return False, f"Database does not correspond"

            cls._import_condorcet(connection, assoc)

        return True, "Data imported"

    @classmethod
    def _import_one_round(cls, connection: Connection, assoc: Dict[int, Candidate]) -> None:
        """Importe des résultats des règles de vote à un tour dans l'élection. Remplit uniquement des scores des candidats. 
        Les classements (un attribut `results` dans `electoral_systems.election.Election`) ne sont pas remplis.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            assoc (Dict[int, people.candidate.Candidate]): Un dictionnaire associant à chaque ID de candidat
                (ID dans la base de données) le candidat correspondant dans l'élection.
                Ceci est nécessaire en raison de la possibilité de divergence de ces IDs.
        """

        cursor = connection.cursor()

        query = "SELECT * FROM results_one_round"
        cursor.execute(query)
        data = cursor.fetchall()

        for candidate_id, voting_rule, score in data:
            candidate = assoc[candidate_id]
            candidate.scores[voting_rule] = int(score)

    @classmethod
    def _import_multi_round(cls, connection: Connection, assoc: Dict[int, int]) -> None:
        """Importe des résultats des règles de vote à plusieurs tour dans l'élection. Remplit uniquement des scores des candidats. 
        Les classements (un attribut `results` dans `electoral_systems.election.Election`) ne sont pas remplis.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            assoc (Dict[int, people.candidate.Candidate]): Un dictionnaire associant à chaque ID de candidat
                (ID dans la base de données) le candidat correspondant dans l'élection.
                Ceci est nécessaire en raison de la possibilité de divergence de ces IDs.
        """

        cursor = connection.cursor()

        # Init lists bases on length
        cursor.execute(
            "SELECT max(round), voting_rule FROM results_multi_round GROUP BY voting_rule")

        nb_rounds = cursor.fetchall()
        for rounds, voting_rule in nb_rounds:
            for candidate in assoc.values():
                candidate.scores[voting_rule] = [0] * (rounds + 1)

        cursor.execute("SELECT * FROM results_multi_round")
        data = cursor.fetchall()
        for candidate_id, voting_rule, round, score in data:
            candidate = assoc[candidate_id]
            candidate.scores[voting_rule][round] = int(score)

    @classmethod
    def _import_condorcet(cls, connection: Connection, assoc: Dict[int, int]) -> None:
        """Importe des résultats des règles de vote Condorcet-cohérentes dans une élection. Remplit uniquement des scores des candidats. 
        Les classements (un attribut `results` dans `electoral_systems.election.Election`) ne sont pas remplis.
        Remplit des résultats des duels entre les candidats (un attribut `duels_scores` dans `electoral_systems.election.Election`).

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            assoc (Dict[int, people.candidate.Candidate]): Un dictionnaire associant à chaque ID de candidat
                (ID dans la base de données) le candidat correspondant dans l'élection.
                Ceci est nécessaire en raison de la possibilité de divergence de ces IDs.
        """

        cursor = connection.cursor()
        # Duels
        cursor.execute("SELECT * FROM condorcet_duels")
        data = cursor.fetchall()

        for winner_id, loser_id, score in data:
            winner = assoc[winner_id]
            loser = assoc[loser_id]
            cls.election.duels_scores[(winner, loser)] = int(score)

        # Scores
        cursor.execute("SELECT * FROM results_condorcet")
        data = cursor.fetchall()

        for candidate_id, voting_rule, score in data:
            candidate = assoc[candidate_id]
            if voting_rule == VotingRulesConstants.CONDORCET:
                candidate.scores[voting_rule] = score
            else:
                candidate.scores[voting_rule] = int(score)

    @classmethod
    def _import_config(cls, connection: Connection, table_missing: bool) -> None:
        """Importe les configurations dans l'élection, i.e. si  
            - la résolution des égalités a été faite par les duels  
            - la démocratie liquide a été activée.  
        Si le tableau `settings` n'est pas présent dans la base des données, désactiver la démocratie liquide et 
        la résolution des égalités par duels.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            table_missing (bool): `True` si le tableau `settings` n'est pas présent dans la base des données, `False` sinon.
        """

        cls.election.liquid_democracy_activated = False
        cls.election.tie_breaker_activated = False

        if table_missing:
            return

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM settings")
        data = cursor.fetchall()

        for parameter, set_value in data:
            match parameter:
                case "liquid_democracy_activated":
                    cls.election.liquid_democracy_activated = bool(set_value)
                case "tie_breaker_activated":
                    cls.election.tie_breaker_activated = bool(set_value)
