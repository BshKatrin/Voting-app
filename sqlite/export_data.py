from sqlite3 import IntegrityError, Connection
from typing import Set

from electoral_systems import Election, VotingRulesConstants

# For docs generation only
__pdoc__ = {
    'ExportData._get_set_check': True,
    'ExportData._one_round_create_table': True,
    'ExportData._one_round_insert': True,
    'ExportData._multi_round_create_table': True,
    'ExportData._multi_round_insert': True,
    'ExportData._condorcet_create_table': True,
    'ExportData._condorcet_insert': True,
    'ExportData._export_config': True,
}


class ExportData:
    """A class providing functionality for data export using SQLite3."""


    election: Election = Election()
    
    EXPORT: str = "E"
    """A constant corresponding to export option."""
    
    @classmethod
    def create_database_people(cls, connection: Connection) -> tuple[bool, str]:
        """Create tables for electors and candidats and exports its data. Election results are **not** exported.

        Args:
            connection (sqlite3.Connection): SQLite connection.

        Returns:
            tuple[bool, str]: A bool `True` if data was exported succesfully, `False` if an error occured. 
                A string with message.
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
        """Create tables for election results and exports results data. Candidates data **must** be exported before.  

        At most 5 tables are created:  
            - A table for **one round** voting rules   
            - A table for **multi-round** voting rules   
            - Two tables for **Condercet-based** voting rules: a table for candidates scores and a table for scores in duels  
            - A table for election settings (liquid democracy, polls etc)  
        Every table is created only if necessary, e.g. if no one round voting rule was chosen
            a table for such results will not be created.

        Args:
            connection (sqlite3.Connection): SQLite connection.

        Returns:
            tuple[bool, str]:  A bool `True` if data was exported succesfully, `False` if an error occured. 
                A string with message.
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

        cls._export_config(connection)
        return True, "Data exported"

    @classmethod
    def _get_set_check(cls, voting_rules_set: Set[str]) -> str:
        """Get a string of an integrity constraint on one or several voting rules.

        Args:
            voting_rules_set (Set[str]): A set of constants related to voting rules. 

        Returns:
            str: An integrity constraint which will be used `CHECK(...)`
        """

        if len(voting_rules_set) == 1:
            return f"= '{str(tuple(voting_rules_set)[0])}'"
        return f"IN {str(tuple(voting_rules_set))}"

    @classmethod
    def _one_round_create_table(cls, connection: Connection, chosen_one_round: Set[str]) -> None:
        """Create a table for one round voting rules results.

        Args:
            connection (sqlite3.Connection): SQLite connection. 
            chosen_one_round (Set[str]): A set of constants related to one round voting rules used in the election.
                Necessary for an integrity constraint.
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
        """Fill the table for one round voting rules results. The table **must** be created before.

        Args:
            connection (sqlite3.Connection): SQLite connection. 
            chosen_one_round (Set[str]): A set of constants related to one round voting rules used in the election.

        Returns:
            bool: `True` if data was inserted succesfully, `False` if an error occurred.
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
        """Create a table for multi-round voting rules results.
        
        Args:
            connection (sqlite3.Connection): SQLite connection.
            chosen_multi_round (Set[str]): A set of constants related to multi-round voting rules used in the election.  
                Necessary of an integrity constraint.
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
        """Fill the table for multi-round voting rules results. The table **must** be created before.

        Args:
            connection (sqlite3.Connection): SQLite connection. 
            chosen_one_round (Set[str]): A set of constants related to multi-round voting rules used in the election.

        Returns:
            bool: `True` if data was inserted succesfully, `False` if an error occurred.
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
        """Create a table for Condorcet-based voting rules results and a table for scores in duels between candidates.

        Args:
            connection (sqlite3.Connection): SQLite connection.
            chosen_condorcet (Set[str]): A set of constants related to Condorcet-based voting rules used in the election.  
                Necessary for an integrity constraint. 
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
        """Fill the table for Condorced-based voting rules results as well as the table for duels scores. 
        These two tables **must** be created before. 

        Args:
            connection (sqlite3.Connection): SQLite connection.
            chosen_condorcet (Set[str]): A set of constants of Condorcet-based voting rules used in the election.

        Returns:
            bool: `True` if all data was inserted succesfully, `False` if an error occured.
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

        # Scores (like in one round)
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

    @classmethod
    def _export_config(cls, connection: Connection) -> None:
        """Export election settings, i.e. if  
            - the tie-break by duels was activated  
            - the liquid democracy was activated   

        Args:
            connection (sqlite3.Connection): SQLite connection.
        """

        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS settings")
        connection.commit()

        table_config = f"""
            CREATE TABLE settings (
                parameter TEXT,
                set_value INTEGER NOT NULL,

                PRIMARY KEY(parameter)
            )
            """
        cursor.execute(table_config)
        connection.commit()

        settings_assoc = [
            ("liquid_democracy_activated", 1 if cls.election.liquid_democracy_activated else 0),
            ("tie_breaker_activated",  1 if cls.election.tie_breaker_activated else 0),
        ]
        cursor.executemany("INSERT INTO settings VALUES (?, ?)", settings_assoc)
        connection.commit()
