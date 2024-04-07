from electoral_systems import Election, VotingRulesConstants


class ExportData:
    election = Election()
    EXPORT = "E"

    @classmethod
    def create_database_people(cls, connection):
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

        cursor.executemany(query, data)
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
        cursor.executemany(query, data)
        connection.commit()

    @classmethod
    def create_database_results(cls, connection):
        # DB for one round voting rules
        chosen_one_round = cls.election.results.keys() & VotingRulesConstants.ONE_ROUND
        if chosen_one_round:
            cls._one_round_create_table(connection, chosen_one_round)
            cls._one_round_insert(connection, chosen_one_round)

        # DB for multi round voting rules
        chosen_multi_round = (
            cls.election.results.keys() & VotingRulesConstants.MULTI_ROUND
        )
        if chosen_multi_round:
            cls._multi_round_create_table(connection, chosen_multi_round)
            cls._multi_round_insert(connection, chosen_multi_round)

        # DB for condorcet voting_rules
        chosen_condorcet = cls.election.results.keys() & VotingRulesConstants.CONDORCET

        if chosen_condorcet:
            cls._condorcet_create_table(connection, chosen_condorcet)
            cls._condorcet_insert(connection, chosen_condorcet)

    @classmethod
    def _one_round_create_table(cls, connection, chosen_one_round):
        cursor = connection.cursor()
        table_scores = f"""
            CREATE TABLE results_one_round (
                candidate_id INTEGER,
                voting_rule TEXT CHECK(voting_rule IN {str(tuple(chosen_one_round))}),
                score REAL,

                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            )
            """

        cursor.execute(table_scores)
        connection.commit()

    @classmethod
    def _one_round_insert(cls, connection, chosen_one_round):
        cursor = connection.cursor()
        query = """INSERT INTO results_one_round(candidate_id, voting_rule, score)
        VALUES(?, ?, ?)"""

        tuples = [
            (c.id, voting_rule, c.scores[voting_rule])
            for voting_rule in chosen_one_round
            for c in cls.election.candidates
        ]

        cursor.executemany(query, tuples)
        connection.commit()

    @classmethod
    def _multi_round_create_table(cls, connection, chosen_multi_round):
        cursor = connection.cursor()
        table_scores = f"""
            CREATE TABLE results_multi_round (
                candidate_id INTEGER,
                voting_rule TEXT CHECK(voting_rule IN {str(tuple(chosen_multi_round))}),
                round INTEGER CHECK(round >= 0),
                score REAL NOT NULL,

                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            )
            """
        cursor.execute(table_scores)
        connection.commit()

    @classmethod
    def _multi_round_insert(cls, connection, chosen_multi_round):
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

        cursor.executemany(query, tuples)
        connection.commit()

    @classmethod
    def _condorcet_create_table(cls, connection, chosen_condorcet):
        cursor = connection.cursor()
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

        table_scores = f"""CREATE TABLE "results_condorcet" (
                candidate_id INTEGER,
                voting_rule TEXT CHECK(voting_rule IN {str(tuple(chosen_condorcet))}),
                score REAL NOT NULL,

                FOREIGN KEY(candidate_id) REFERENCES candidates(id)
            )
            """

        cursor.execute(table_scores)
        connection.commit()

    @classmethod
    def _condorcet_insert(cls, connection, chosen_condorcet):
        # Duels
        cursor = connection.cursor()
        query = """INSERT INTO condorcet_duels(winner_id, loser_id, score)
        VALUES(?, ?, ?)"""

        tuples = [
            (pair[0].id, pair[1].id, score)
            for pair, score in cls.election.condorcet_graph_info.items()
        ]

        cursor.executemany(query, tuples)
        connection.commit()

        # Scores (like in one round)
        query = """INSERT INTO results_condorcet(candidate_id, voting_rule, score)
        VALUES(?, ?, ?)"""

        tuples = [
            (c.id, voting_rule, c.scores[voting_rule])
            for voting_rule in chosen_condorcet
            for c in cls.election.candidates
        ]

        cursor.executemany(query, tuples)
        connection.commit()
