from sqlite3 import Connection
from typing import Set, Dict

from electoral_systems import Election, VotingRulesConstants
from people import Candidate, Elector

# For docs generation only
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
    """A class which provides functionnality for data import. SQLite3 is used."""

    election: Election = Election()
    IMPORT: str = "I"

    @classmethod
    def _check_tables(cls, tables_to_check: Set[str], existing_tables: Set[str]) -> tuple[bool, Set[str]]:
        """Verify if tables in `tables_to_check` exist in database. Tables in database are listed in `existing_tables`.

        Args:
            tables_to_check (Set[str]): Table names whose existence should be verified.
            existing_tables (Set[str]): Table names that exist in database.

        Returns:
            tuple[bool, Set[str]]: A bool `True` if at least one table is missing in database and a set of missing table names.
                Otherwise, a bool `False` if all tables exist in DB, a set is empty in that case.
        """

        missing_tables = tables_to_check - (tables_to_check & existing_tables)
        return (bool(missing_tables), missing_tables)

    @classmethod
    def _get_existing_tables(cls, connection: Connection) -> Set[str]:
        """Get names of all existing tables in database. 

        Args:
            connection (sqlite3.Connection): SQLite connection.

        Returns:
            Set[str]: A set of table names.
        """

        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        return {row[0] for row in cursor.fetchall()}

    @classmethod
    def _check_columns(cls, connection: Connection, tables_cols: Dict[str, tuple[str, str]]) -> bool:
        """Verify column names and their type affinity.

        Args:
            connection (sqlite3.Connection): SQLite connection.
            tables_cols (Dict[str, tuple[str, str]]): A dictionary whose keys are table names (existing in database),
                and values are column names ant type affinity which should be verified.

        Returns:
            bool: `True` if every table all specified columns with the correct type affinity. `False` otherwise.
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
        """Verify column names and their type affinity in tables for electors and candidates.

        Args:
            connection (sqlite3.Connection): SQLite connection.

        Returns:
            bool: `True` if every table has all necessary columns with the correct type affinity. 
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
        """Import data to the election from the database. Electors and candidates data are imported in any case. 
        Results data are imported only if necessary. Make all necessary verification on tables and its columns.

        Args:
            connection (sqlite3.Connection): SQLite connection.
            with_results (bool): `True` is results should be imported. `False`, otherwise.

        Returns:
            tuple[bool, str]: Un booléen `True` si les données ont été importées avec succès, `False` si l'erreur est survenue.
                Une chaîne de caractères avec le message.
        """

        if with_results:
            return cls.import_people_with_results(connection)
        return cls.import_people_no_results(connection)

    @classmethod
    def import_people_no_results(cls, connection: Connection) -> tuple[bool, str]:
        """Import data (candidates, electors only) in the election from the database.
        Make necessary verifications on tables and columns.

        Args:
            connection (sqlite3.Connection): SQLite connection.

        Returns:
            tuple[bool, str]: A bool `True` if data was imported succesfully, `False` if an error occurred.
                A string with message.
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
        """Import data (candidates, electors, results) to the election from the database. Make necessary verification on 
        tables and its columns. Import election settings if such table exists. Delete all existing data in the election.

        Args:
            connection (sqlite3.Connection): SQLite connection.

        Returns:
            tuple[bool, str]: A bool `True` if data was imported succesfully, `False` if an error occurred.
                A string with message.
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
        """Import results of each voting rule existing in the database to the election. 
        Make necessary verifications on tables and its columns. 

        Args:
            connection (sqlite3.Connection): SQLite connection.
            existing_tables (Set[str]): A set of names of tables existing in database.
            assoc (Dict[int, people.candidate.Candidate]): A dictionary associating each candidate ID
                (ID in database) a candidate in the election. Necessary because a there is a possiblity of divergence of these IDs.

        Returns:
            tuple[bool, str]: A bool `True` if data was imported succesfully, `False` if an error occurred.
                A string with message.
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
        """Import results of one round voting rules to the election. Fill only candidates scores. 
        The rankings (an attribute `results` dans `electoral_systems.election.Election`) are not filled.


        Args:
            connection (sqlite3.Connection): SQLite connection.
            assoc (Dict[int, people.candidate.Candidate]): A dictionary associating each candidate ID
                (ID in database) a candidate in the election. Necessary because a there is a possiblity of divergence of these IDs.
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
        """Import results of multi-round voting rules to the election. Fill only candidates scores. 
        The rankings (an attribute `results` in `electoral_systems.election.Election`) are not filled.

        Args:
            connection (sqlite3.Connection): SQLite connection.
            assoc (Dict[int, people.candidate.Candidate]): A dictionary associating each candidate ID
                (ID in database) a candidate in the election. Necessary because a there is a possiblity of divergence of these IDs.
        """

        cursor = connection.cursor()

        # Init lists based on length
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
        """Import results of Condorcet-based voting rules to the election. Fill only candidates scores.
        The ranking (an attribute `results` in `electoral_systems.election.Election`) are not filled.
        Fill results of duels between candidates (un attribute `duels_scores` in `electoral_systems.election.Election`).

        Args:
            connection (sqlite3.Connection): SQLite connection.
            assoc (Dict[int, people.candidate.Candidate]): A dictionary associating each candidate ID
                (ID in database) a candidate in the election. Necessary because a there is a possiblity of divergence of these IDs.
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
        """Import settings to the election, i.e. if  
            - the tie-break by duels was activated  
            - the liquid democracy was activated

        If the table `settings` does not exist in database, desactivate the liquid democracy and the tie-break by duels.

        Args:
            connection (sqlite3.Connection): SQLite connection.
            table_missing (bool): `True` if the table `settings` does not exist in the database, `False` otherwise.
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
