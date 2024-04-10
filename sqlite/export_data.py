from sqlite3 import IntegrityError, Connection
from typing import Set

from electoral_systems import Election, VotingRulesConstants


class ExportData:
    """Une classe qui fournit la fonctionnalité nécessaires pour une exportation des données d'une élection.
    SQLite3 est utilisé."""

    election = Election()
    EXPORT = "E"

    @classmethod
    def create_database_people(cls, connection: Connection) -> tuple[bool, str]:
        """Créer des tableaux des électeurs et des candidats d'une élection et exporter les données.

        Args:
            connection (sqlite3.Connection): une connection SQLite.

        Returns:
            tuple[bool, str]: Un booléen True si les données ont été exportées avec succès, False si l'erreur est survenue.
            Une chaîne de caractères avec le message.
        """

        cursor = connection.cursor()

        cursor.executescript(
            "DROP TABLE IF EXISTS electors; DROP TABLE IF EXISTS candidates"
        )
        connection.commit()

        tables = """CREATE TABLE electors (
            id INTEGER PRIMARY KEY,
            x REAL CHECK(x <= 1 AND x >= -1),
            y REAL CHECK(y <= 1 AND y >= -1),
            weight INTEGER CHECK(weight >= 0),
            knowledge REAL CHECK(knowledge <= 1 AND knowledge >= 0)
        );
        CREATE TABLE candidates (
            id INTEGER PRIMARY KEY,
            x REAL CHECK(x <= 1 AND x >= -1),
            y REAL CHECK(y <= 1 AND y >= -1),
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            dogmatism REAL CHECK(dogmatism <= 1 AND dogmatism >= 0),
            opposition REAL CHECK(opposition <= 1 AND opposition >= 0)
        );
        """

        cursor.executescript(tables)
        connection.commit()

        query = """
            INSERT INTO electors(id, x, y, weight, knowledge)
            VALUES (?, ?, ?, ?, ?)
            """

        data = [
            (e.id, e.position[0], e.position[1], e.weight, e.knowledge)
            for e in cls.election.electors
        ]
        try:
            cursor.executemany(query, data)
        except IntegrityError:
            return False, "Data does not corresponds to constraints"

        connection.commit()

        # for candidate in candidates:
        query = """
            INSERT INTO candidates(id, x, y, first_name, last_name, dogmatism, opposition)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

        data = [
            (
                c.id,
                c.position[0],
                c.position[1],
                c.first_name,
                c.last_name,
                c.dogmatism,
                c.opposition,
            )
            for c in cls.election.candidates
        ]
        try:
            cursor.executemany(query, data)
        except IntegrityError:
            return False, "Data does not corresponds to constraints"

        connection.commit()

        return True, "Date exported"

    @classmethod
    def create_database_results(cls, connection: Connection) -> tuple[bool, str]:
        """Créer des tableaux des résultats d'une élection et exporter les données.
        Au plus il peut exister 4 tableaux:
            - Un tableau pour des règles du vote à un tour
            - Un tableau pour des règles du vote à plusieurs tours
            - Deux tableaux pour des règles du vote Condorcet-cohérentes. Un tableau pour des scores des candidats, un tableau pour
            des scores dans les duels.
        Chaque tableau est créé uniquement si nécessaire, e.g. si aucune règle du vote à un tour n'étais pas utilisée lors d'une élection,
        il ne sera pas crée.

        Args:
            connection (sqlite3.Connection): une connection SQLite.

        Returns:
            tuple[bool, str]: Un booléen True si les données ont été exportées avec succès, False si l'erreur est survenue.
            Une chaîne de caractères avec le message.
        """

        # DB for one round voting rules
        chosen_one_round = cls.election.results.keys() & VotingRulesConstants.ONE_ROUND
        status = True

        if chosen_one_round:
            cls._one_round_create_table(connection, chosen_one_round)
            status = cls._one_round_insert(connection, chosen_one_round)
        if not status:
            return False, "Results of voting rules (1 round) do not correspond to constraints"

        # DB for multi round voting rules
        chosen_multi_round = (
            cls.election.results.keys() & VotingRulesConstants.MULTI_ROUND
        )
        if chosen_multi_round:
            cls._multi_round_create_table(connection, chosen_multi_round)
            status = cls._multi_round_insert(connection, chosen_multi_round)
        if not status:
            return False, "Results of voting rules (multi round) do not correspond to constraints"

        # DB for condorcet voting_rules
        chosen_condorcet = cls.election.results.keys() & VotingRulesConstants.CONDORCET

        if chosen_condorcet:
            cls._condorcet_create_table(connection, chosen_condorcet)
            status = cls._condorcet_insert(connection, chosen_condorcet)
        if not status:
            return False, "Results of voting rules (Condorcet) do not correspond to constraints"

        return True, "Data exported"

    @classmethod
    def _get_set_check(cls, voting_rules_set: Set[str]) -> str:
        """Retourner une chaîne de caractères d'une contrainte d'intégrité sur une règle du vote.

        Args:
            voting_rules_set(Set[str]): Un ensemble des constantes associées aux règles du vote.
        Returns:
            str: Une constrainte d'intégrité utilisé dand 'CHECK(...)'
        """
        if len(voting_rules_set) == 1:
            return f"= '{str(tuple(voting_rules_set)[0])}'"
        return f"IN {str(tuple(voting_rules_set))}"

    @classmethod
    def _one_round_create_table(cls, connection: Connection, chosen_one_round: Set[str]) -> None:
        """Créer un tableau pour des résultats des règle du vote à un tour.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            chosen_one_round (Set[str]): Un ensemble des règles du vote à un tour utilisées dans une élection.
                Nécessaire pour une contrainte d'intégrité.
        """

        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS results_one_round")
        connection.commit()

        table_scores = f"""
            CREATE TABLE results_one_round (
                candidate_id INTEGER,
                voting_rule TEXT CHECK(voting_rule {ExportData._get_set_check(chosen_one_round)}),
                score REAL,

                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            )
            """
        cursor.execute(table_scores)
        connection.commit()

    @classmethod
    def _one_round_insert(cls, connection: Connection, chosen_one_round: Set[str]) -> bool:
        """Remplir le tableau pour des résultats des règle du vote à un tour.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            chosen_one_round (Set[str]): Un ensemble des règles du vote à un tour utilisées dans une élection.

        Returns:
            bool: True si les données ont été insérées, False si l'erreur est survenue.
        """

        cursor = connection.cursor()
        query = """INSERT INTO results_one_round(candidate_id, voting_rule, score)
        VALUES(?, ?, ?)"""

        tuples = [
            (c.id, voting_rule, c.scores[voting_rule])
            for voting_rule in chosen_one_round
            for c in cls.election.candidates
        ]

        try:
            cursor.executemany(query, tuples)
        except IntegrityError:
            return False

        connection.commit()
        return True

    @classmethod
    def _multi_round_create_table(cls, connection: Connection, chosen_multi_round: Set[str]) -> None:
        """Créer un tableau pour des résultats des règle du vote à plusiers tours

        Args:
            connection(sqlite3.Connection): Une connection SQLite.
            chosen_multi_round(Set[str]): Un ensemble des règles du vote à plusieurs tours utilisées dans une élection.
                Nécessaire pour une contrainte d'intégrité.
        """

        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS results_multi_round")
        connection.commit()

        table_scores = f"""
            CREATE TABLE results_multi_round (
                candidate_id INTEGER,
                voting_rule TEXT CHECK(voting_rule {ExportData._get_set_check(chosen_multi_round)}),
                round INTEGER CHECK(round >= 0),
                score REAL NOT NULL,

                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            )
            """
        cursor.execute(table_scores)
        connection.commit()

    @classmethod
    def _multi_round_insert(cls, connection: Connection, chosen_multi_round: Set[str]) -> bool:
        """Remplir le tableau pour des résultats des règle du vote à plusieurs tours.

        Args:
            connection (sqlite3.Connection): Une connection SQLite.
            chosen_multi_round (Set[str]): Un ensemble des règles du vote à plusieurs tours utilisées dans une élection.

        Returns:
            bool: True si les données ont été insérées, False si l'erreur est survenue.
        """

        cursor = connection.cursor()
        query = """INSERT INTO results_multi_round(candidate_id, voting_rule, round, score)
        VALUES(?, ?, ?, ?)
        """

        tuples = [
            (c.id, voting_rule, round, c.scores[voting_rule][round])
            for voting_rule in chosen_multi_round
            for c in cls.election.candidates
            for round in range(len(c.scores[voting_rule]))
        ]
        try:
            cursor.executemany(query, tuples)
        except IntegrityError:
            return False
        connection.commit()
        return True

    @classmethod
    def _condorcet_create_table(cls, connection: Connection, chosen_condorcet: Set[str]) -> None:
        """Créer un tableau pour des résultats des règles du vote Condorcet-cohérentes et des duels entre les candidats.

        Args:
            connection(sqlite3.Connection): Une connection SQLite.
            chosen_condorcet (Set[str]): Un ensemble des règles du vote Condorcet-cohérentes utilisées dans une élection.
                Nécessaire pour une contrainte d'intégrité.
        """

        cursor = connection.cursor()
        cursor.executescript(
            "DROP TABLE IF EXISTS condorcet_duels;DROP TABLE IF EXISTS results_condorcet"
        )
        connection.commit()

        table_duels = f"""
            CREATE TABLE condorcet_duels (
                winner_id INTEGER NOT NULL,
                loser_id INTEGER NOT NULL,
                score REAL NOT NULL,

                FOREIGN KEY(winner_id) REFERENCES candidates(id),
                FOREIGN KEY(loser_id) REFERENCES candidates(id)
            )
            """
        cursor.execute(table_duels)

        connection.commit()
        table_scores = f"""CREATE TABLE results_condorcet (
                candidate_id INTEGER,
                voting_rule TEXT CHECK(voting_rule {ExportData._get_set_check(chosen_condorcet)}),
                score REAL NOT NULL,

                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            )
            """

        cursor.execute(table_scores)
        connection.commit()

    @classmethod
    def _condorcet_insert(cls, connection: Connection, chosen_condorcet: Set[str]) -> bool:
        """Remplir le tableau pour des scores des règles du vote Condorcet-cohérentes et des duels.

        Args:
            connection (sqlite3.Connection). Une connection SQLite.
            chosen_condorcet (Set[str]): Un ensemble des règles du vote Condorcet-cohérentes utilisées dans une élection.

        Returns:
            bool: True si les données ont été insérées, False si l'erreur est survenue.
        """

        # Duels
        cursor = connection.cursor()
        query = """INSERT INTO condorcet_duels(winner_id, loser_id, score)
        VALUES(?, ?, ?)"""

        tuples = [
            (pair[0].id, pair[1].id, score)
            for pair, score in cls.election.duels_scores.items()
        ]
        try:
            cursor.executemany(query, tuples)
        except IntegrityError:
            return False
        connection.commit()

        # Scores (comme à un tour)
        query = """INSERT INTO results_condorcet(candidate_id, voting_rule, score)
        VALUES(?, ?, ?)"""

        tuples = [
            (c.id, voting_rule, c.scores[voting_rule])
            for voting_rule in chosen_condorcet
            for c in cls.election.candidates
        ]
        try:
            cursor.executemany(query, tuples)
        except IntegrityError:
            return False
        connection.commit()
        return True
