import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from electoral_systems.voting_rules import condorcet
from electoral_systems.voting_rules.constants import CONDORCET_SIMPLE, CONDORCET_COPELAND, CONDORCET_SIMPSON
from electoral_systems.utls import IdIterator
from electoral_systems.voting_rules.utls import set_duels_scores
from people.elector import Elector
from people.candidate import Candidate


class TestCondorcet(unittest.TestCase):

    def setUp(self):
        self.id_iter = IdIterator(0)
        p = (0, 0)
        # Position n'affecte pas des résultats dans ce cas (candidates_ranked sera définie manuellement)
        self.c0 = Candidate(id=next(self.id_iter), position=p, first_name="A", last_name="B")
        self.c1 = Candidate(id=next(self.id_iter), position=p, first_name="C", last_name="D")
        self.c2 = Candidate(id=next(self.id_iter), position=p, first_name="E", last_name="F")
        self.c3 = Candidate(id=next(self.id_iter), position=p, first_name="G", last_name="H")
        self.candidates = [self.c3, self.c2, self.c1, self.c0]

    def test_condorcet_simple_no_winner(self):
        p = (0, 0)

        # Position n'affecte pas des résultats dans ce cas (candidates_ranked est définie manuellement)
        e0 = Elector(id=next(self.id_iter), position=p, candidates_ranked=[self.c0, self.c1, self.c3, self.c2])
        e1 = Elector(id=next(self.id_iter), position=p, candidates_ranked=[self.c3, self.c1, self.c2, self.c0])
        e2 = Elector(id=next(self.id_iter), position=p, candidates_ranked=[self.c2, self.c0, self.c1, self.c3])
        electors = [e0, e1, e2]

        duels = set_duels_scores(electors, self.candidates)

        duels_test = {
            (self.c0, self.c1): 2,
            (self.c2, self.c0): 2,
            (self.c0, self.c3): 2,
            (self.c1, self.c2): 2,
            (self.c1, self.c3): 2,
            (self.c3, self.c2): 2,
        }
        self.assertEqual(duels, duels_test)

        # Vérification d'un classement (résolution des égalités par ordre alphabétique)
        self.assertEqual(
            condorcet.apply_condorcet_simple(electors, self.candidates, duels), [self.c0, self.c1, self.c2, self.c3]
        )
        # Vérification des scores
        self.assertEqual(self.c0.scores[CONDORCET_SIMPLE], 2)
        self.assertEqual(self.c1.scores[CONDORCET_SIMPLE], 2)
        self.assertEqual(self.c2.scores[CONDORCET_SIMPLE], 1)
        self.assertEqual(self.c3.scores[CONDORCET_SIMPLE], 1)

    def test_condorcet_simple_winner(self):
        p = (0, 0)

        # Position n'affecte pas des résultats dans ce cas (candidates_ranked est définie manuellement)
        e0 = Elector(id=next(self.id_iter), position=p, candidates_ranked=[self.c0, self.c1, self.c3, self.c2])
        e1 = Elector(id=next(self.id_iter), position=p, candidates_ranked=[self.c3, self.c1, self.c0, self.c2])
        e2 = Elector(id=next(self.id_iter), position=p, candidates_ranked=[self.c2, self.c0, self.c1, self.c3])
        electors = [e0, e1, e2]

        duels = set_duels_scores(electors, self.candidates)

        duels_test = {
            (self.c0, self.c1): 2,
            (self.c0, self.c2): 2,
            (self.c0, self.c3): 2,
            (self.c1, self.c2): 2,
            (self.c1, self.c3): 2,
            (self.c3, self.c2): 2,
        }
        self.assertEqual(duels, duels_test)

        # Vérification d'un classement (résolution des égalités par ordre alphabétique)
        self.assertEqual(
            condorcet.apply_condorcet_simple(electors, self.candidates, duels), [self.c0, self.c1, self.c3, self.c2]
        )
        # Vérification des scores
        self.assertEqual(self.c0.scores[CONDORCET_SIMPLE], 3)  # Gagnant
        self.assertEqual(self.c1.scores[CONDORCET_SIMPLE], 2)
        self.assertEqual(self.c2.scores[CONDORCET_SIMPLE], 0)
        self.assertEqual(self.c3.scores[CONDORCET_SIMPLE], 1)

    def test_condorcet_copeland(self):

        # Position n'affecte pas des résultats dans ce cas (candidates_ranked est définie manuellement)
        p = (0, 0)
        electors = []
        for _ in range(2):
            ranking = [self.c0, self.c1, self.c3, self.c2]
            electors.append(Elector(id=next(self.id_iter), position=p, candidates_ranked=ranking))

        electors.append(Elector(id=next(self.id_iter), position=p,
                        candidates_ranked=[self.c3, self.c1, self.c2, self.c0]))

        for _ in range(2):
            ranking = [self.c2, self.c0, self.c1, self.c3]
            electors.append(Elector(id=next(self.id_iter), position=p, candidates_ranked=ranking))

        duels = set_duels_scores(electors, self.candidates)

        duels_test = {
            (self.c0, self.c1): 4,
            (self.c2, self.c0): 3,
            (self.c0, self.c3): 4,
            (self.c1, self.c2): 3,
            (self.c1, self.c3): 4,
            (self.c3, self.c2): 3,
        }
        self.assertEqual(duels, duels_test)

        # Vérification d'un classement (résolution des égalités par ordre alphabétique)
        self.assertEqual(
            condorcet.apply_condorcet_copeland(electors, self.candidates, duels), [self.c0, self.c1, self.c2, self.c3]
        )

        # Vérification des scores
        self.assertEqual(self.c0.scores[CONDORCET_COPELAND], 2)
        self.assertEqual(self.c1.scores[CONDORCET_COPELAND], 2)
        self.assertEqual(self.c2.scores[CONDORCET_COPELAND], 1)
        self.assertEqual(self.c3.scores[CONDORCET_COPELAND], 1)

    def test_condorcet_simpson(self):

        # Position n'affecte pas des résultats dans ce cas (candidates_ranked est définie manuellement)
        p = (0, 0)
        electors = []
        for _ in range(2):
            ranking = [self.c0, self.c1, self.c3, self.c2]
            electors.append(Elector(id=next(self.id_iter), position=p, candidates_ranked=ranking))

        electors.append(Elector(id=next(self.id_iter), position=p,
                        candidates_ranked=[self.c3, self.c1, self.c2, self.c0]))

        for _ in range(2):
            ranking = [self.c2, self.c0, self.c1, self.c3]
            electors.append(Elector(id=next(self.id_iter), position=p, candidates_ranked=ranking))

        duels = set_duels_scores(electors, self.candidates)

        duels_test = {
            (self.c0, self.c1): 4,
            (self.c2, self.c0): 3,
            (self.c0, self.c3): 4,
            (self.c1, self.c2): 3,
            (self.c1, self.c3): 4,
            (self.c3, self.c2): 3,
        }
        self.assertEqual(duels, duels_test)

        # Vérification d'un classement (résolution des égalités par ordre alphabétique)
        self.assertEqual(
            condorcet.apply_condorcet_simpson(electors, self.candidates, duels), [self.c0, self.c2, self.c1, self.c3]
        )

        # Vérification des scores
        self.assertEqual(self.c0.scores[CONDORCET_SIMPSON], 3)
        self.assertEqual(self.c1.scores[CONDORCET_SIMPSON], 4)
        self.assertEqual(self.c2.scores[CONDORCET_SIMPSON], 3)
        self.assertEqual(self.c3.scores[CONDORCET_SIMPSON], 4)
