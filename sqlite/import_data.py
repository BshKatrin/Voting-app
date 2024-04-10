from sqlite3 import Connection
from typing import Set, Dict

from electoral_systems import Election
from people import Candidate, Elector


class ImportData:
    """Une classe qui fournit la fonctionnalité nécessaires pour une importation des données d'une élection.
    SQLite3 est utilisé."""

    election = Election()
    IMPORT = "I"

    # Check that table corresponds
    @classmethod
    def _check_tables(cls, tables_to_check: Set[str], existing_tables: Set[str]) -> tuple[bool, Set[str]]:
        """Vérifier que les tableaux dans `tables_to_check` sont présents dans une base des données qui
        contient `existing_tables`.

        Args:
            tables_to_check (Set[str]): Des noms tableaux dont l'existance il faut vérifier
            existing_tables (Set[str]): Des noms des tableaux qui existe dans une base des données.
        """

        missing_tables = tables_to_check - (tables_to_check & existing_tables)
        return (bool(missing_tables), missing_tables)

    @classmethod
    def _get_existing_tables(cls, connection: Connection) -> Set[str]:
        """Retourner des noms des tableaux qui existent dans une base des données.

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
        """Vérifier le noms des colonnes et leurs affinités de type.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            tables_cols (Dict[str, tuple[str, str]]): Un dictionnnaire dont les clés sont des noms des tableaux qui existent
            dans une base des données. Des valeurs sont des noms des colonnes et leurs affinités de type qu'il faut vérifier.

        Returns:
            bool: True si dans chaque tableau il existe bien des colonnes données avec la bonne affinité de type. Sinon, False.
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
        """Vérifier des colonnes et leurs affinités de type pour des tableaux des candidats et des électeurs.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.

        Returns:
            bool: True si pour chaque tableau il existe bien des colonnes avec la bonne affinité de type.
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
        """Importer des données dans une élection à partir de la base des données. Une fonction fait les vérifications
        nécessaires des tableaux et des colonnes.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            with_results (bool): True s'il faut importer avec des résultats. False, s'il faut importer sans des résultats.

        Returns:    
            tuple[bool, str]: Un booléen True si les données ont été importées avec succès, False si l'erreur est survenue.
            Une chaîne de caractères avec le message.
        """

        if with_results:
            return cls.import_people_with_results(connection)
        return cls.import_people_no_results(connection)

    @classmethod
    def import_people_no_results(cls, connection: Connection) -> tuple[bool, str]:
        """Importer des données (candidats, électeurs uniquement) dans une élection à partir de la base des données.
        Une fonction fait les vérifications nécessaires des tableaux et des colonnes.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.

        Returns:    
            tuple[bool, str]: Un booléen True si les données ont été importées avec succès, False si l'erreur est survenue.
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
        """Importer des données (candidats, électeurs, résultats) dans une élection à partir de la base des données.
        Une fonction fait les vérifications nécessaires des tableaux et des colonnes.
        Supprime toutes les données existantes d'une élection.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.

        Returns:    
            tuple[bool, str]: Un booléen True si les données ont été importées avec succès, False si l'erreur est survenue.
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
        return cls._import_results(connection, existing_tables, candidates_id_assoc)

    @classmethod
    def _import_results(cls, connection: Connection, existing_tables: Set[str], assoc: Dict[int, Candidate]) -> tuple[bool, str]:
        """Importer des résultats de chaque règle du vote présente dans une base des données dans une élection.
        Une fonction fait les vérifications nécessaires des tableaux et des colonnes.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            existing_tables (Set[str]): Un ensemble des noms des tableaux qui existent dans une base des données.
            assoc: Dict[int, people.candidate.Candidate]: Un dictionnaire qui associe à chaque ID d'un candidat
            (ID dans une base des données) un candidat dans une élection. Nécessaire à cause de la possiblité de divergences
            des ces IDs.

        Returns:    
            tuple[bool, str]: Un booléen True si les données ont été importées avec succès, False si l'erreur est survenue.
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
        """Importer des résultats des règles du vote à un tour dans une élection. Une fonction fait les vérifications
        nécessaires des tableaux et des colonnes. Une fonction remplie uniquement des scores des candidats, elle 
        ne remplit pas un classement (un attribut `results` dans une `election`).

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            assoc: Dict[int, people.candidate.Candidate]: Un dictionnaire qui associe à chaque ID d'un candidat
            (ID dans une base des données) un candidat dans une élection. Nécessaire à cause de la possiblité de divergences
            des ces IDs.

        Returns:    
            tuple[bool, str]: Un booléen True si les données ont été importées avec succès, False si l'erreur est survenue.
            Une chaîne de caractères avec le message.
        """

        cursor = connection.cursor()

        query = "SELECT * FROM results_one_round"
        cursor.execute(query)
        data = cursor.fetchall()

        for candidate_id, voting_rule, score in data:
            candidate = assoc[candidate_id]
            candidate.scores[voting_rule] = score

    @classmethod
    def _import_multi_round(cls, connection: Connection, assoc: Dict[int, int]) -> None:
        """Importer des résultats des règles du vote à plusieurs tour dans une élection. Une fonction fait les vérifications
        nécessaires des tableaux et des colonnes. Une fonction remplie uniquement des scores des candidats, elle 
        ne remplit pas un classement (un attribut `results` dans une `election`).

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            assoc: Dict[int, people.candidate.Candidate]: Un dictionnaire qui associe à chaque ID d'un candidat
            (ID dans une base des données) un candidat dans une élection. Nécessaire à cause de la possiblité de divergences
            des ces IDs.

        Returns:    
            tuple[bool, str]: Un booléen True si les données ont été importées avec succès, False si l'erreur est survenue.
            Une chaîne de caractères avec le message.
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
            candidate.scores[voting_rule][round] = score

    @classmethod
    def _import_condorcet(cls, connection: Connection, assoc: Dict[int, int]) -> None:
        """Importer des résultats des règles du vote Condorcet-cohérentes dans une élection. Une fonction fait les vérifications
        nécessaires des tableaux et des colonnes. Une fonction remplie des scores des candidats, elle 
        ne remplit pas un classement (un attribut `results` dans une `election`). De plus, la fonction remplie des résultats des duels
        entre les candidats (un attribut `duels_scores` dans `election`).

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            assoc: Dict[int, people.candidate.Candidate]: Un dictionnaire qui associe à chaque ID d'un candidat
            (ID dans une base des données) un candidat dans une élection. Nécessaire à cause de la possiblité de divergences
            des ces IDs.

        Returns:    
            tuple[bool, str]: Un booléen True si les données ont été importées avec succès, False si l'erreur est survenue.
            Une chaîne de caractères avec le message.
        """

        cursor = connection.cursor()
        # Duels
        cursor.execute("SELECT * FROM condorcet_duels")
        data = cursor.fetchall()

        for winner_id, loser_id, score in data:
            winner = assoc[winner_id]
            loser = assoc[loser_id]
            cls.election.duels_scores[(winner, loser)] = score

        # Scores
        cursor.execute("SELECT * FROM results_condorcet")
        data = cursor.fetchall()

        for candidate_id, voting_rule, score in data:
            candidate = assoc[candidate_id]
            candidate.scores[voting_rule] = score
