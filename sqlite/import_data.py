from electoral_systems import Election, VotingRulesConstants
from people import Candidate, Elector


class ImportData:
    election = Election()
    IMPORT = "I"

    # Check that table corresponds
    @classmethod
    def _check_tables(cls, tables_to_check, existing_tables):
        missing_tables = tables_to_check - (tables_to_check & existing_tables)
        return (bool(missing_tables), missing_tables)

    @classmethod
    def _get_existing_tables(cls, connection):
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        return {row[0] for row in cursor.fetchall()}

    @classmethod
    def import_people(cls, connection, with_results):
        if with_results:
            return cls.import_people_with_results(connection)
        else:
            return cls.import_people_no_results(connection)

    # Return (True, msg) if saved, (False, msg) if not
    @classmethod
    def import_people_no_results(cls, connection):
        # Necessary cause of ID (which is unique) and hash
        # cls.election.delete_all_data()
        existing_tables = cls._get_existing_tables(connection)
        missing, missing_tables = cls._check_tables(
            {"candidates", "electors"}, existing_tables
        )
        if missing:
            return False, f"Tables {missing_tables} are not found"

        cursor = connection.cursor()

        cursor.execute("SELECT x, y, first_name, last_name FROM candidates")
        candidates_data = cursor.fetchall()

        for x, y, first_name, last_name in candidates_data:
            cls.election.add_candidate(
                Candidate(position=(x, y), first_name=first_name, last_name=last_name)
            )

        cursor.execute("SELECT x, y, weight, knowledge FROM electors")
        electors_data = cursor.fetchall()

        for x, y, weight, knowledge in electors_data:
            cls.election.add_elector(
                Elector(
                    candidates=cls.election.candidates,
                    position=(x, y),
                    weight=weight,
                    knowledge=knowledge,
                )
            )
        return True, "Data imported"

    @classmethod
    def import_people_with_results(cls, connection):
        cls.election.delete_all_data()

        existing_tables = cls._get_existing_tables(connection)
        missing, missing_tables = cls._check_tables(
            {"candidates", "electors"}, existing_tables
        )
        if missing:
            return False, f"Tables {missing_tables} are not found"

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM candidates")
        candidates_data = cursor.fetchall()

        # id : candidate
        candidates_id_assoc = dict()

        for id, x, y, first_name, last_name in candidates_data:
            new_candidate = Candidate(
                id=id, position=(x, y), first_name=first_name, last_name=last_name
            )
            cls.election.add_candidate(new_candidate)
            candidates_id_assoc[id] = new_candidate

        cursor.execute("SELECT * FROM electors")
        electors_data = cursor.fetchall()

        for id, x, y, weight, knowledge in electors_data:
            cls.election.add_elector(
                Elector(
                    id=id,
                    candidates=cls.election.candidates,
                    position=(x, y),
                    weight=weight,
                    knowledge=knowledge,
                )
            )
        return cls._import_results(connection, existing_tables, candidates_id_assoc)

    @classmethod
    def _import_results(cls, connection, existing_tables, assoc):
        # Check that tables related to scores exists
        _, missing_tables = cls._check_tables(
            {"results_one_round", "results_multi_round", "results_condorcet"},
            existing_tables,
        )

        if len(missing_tables) == 3:
            return False, "No tables related to scores found"

        if "results_one_round" in existing_tables:
            cls._import_one_round(connection, assoc)

        if "results_multi_round" in existing_tables:
            cls._import_multi_round(connection, assoc)

        if (
            "results_condorcet" in existing_tables
            and "condorcet_duels" in existing_tables
        ):
            cls._import_condorcet(connection, assoc)

        return True, "Data imported"

    @classmethod
    def _import_one_round(cls, connection, assoc):
        cursor = connection.cursor()

        query = "SELECT * FROM results_one_round"
        cursor.execute(query)
        data = cursor.fetchall()

        for candidate_id, voting_rule, score in data:
            candidate = assoc[candidate_id]
            candidate.scores[voting_rule] = score

    @classmethod
    def _import_multi_round(cls, connection, assoc):
        cursor = connection.cursor()

        # Init lists bases on length
        cursor.execute("SELECT max(round), name FROM results_multi_round GROUP BY name")

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
    def _import_condorcet(cls, connection, assoc):
        error, missing_table = cls._check_tables(connection, "condorcet_duels")
        if error:
            return False, f"Table {missing_table} not found"

        cursor = connection.cursor()
        # Duels
        cursor.execute("SELECT * FROM condorcet_duels")
        data = cursor.fetchall()

        for winner_id, loser_id, score in data:
            winner = assoc[winner_id]
            loser = assoc[loser_id]
            cls.election.condorcet_graph_info[(winner, loser)] = score

        # Scores
        cursor.execute("SELECT * FROM results_condorcet")
        data = cursor.fetchall()

        for candidate_id, voting_rule, score in data:
            candidate = assoc[candidate_id]
            candidate.scores[voting_rule] = score
