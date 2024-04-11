import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from electoral_systems.voting_rules import plurality
from electoral_systems.voting_rules.constants import PLURALITY_SIMPLE, PLURALITY_2_ROUNDS
from electoral_systems.utls import IdIterator
from electoral_systems.voting_rules.utls import set_duels_scores
from people.elector import Elector
from people.candidate import Candidate


class TestPlurality(unittest.TestCase):

    def setUp(self):
        self.id_iter = IdIterator(0)

        # Position n'affecte pas des résultats dans ce cas (self.candidates sera définie manuellement)
        self.c0 = Candidate(id=next(self.id_iter), position=(0, 0), first_name="A", last_name="A")
        self.c1 = Candidate(id=next(self.id_iter), position=(0, 0), first_name="B", last_name="B")
        self.c2 = Candidate(id=next(self.id_iter), position=(0, 0), first_name="C", last_name="C")
        self.c3 = Candidate(id=next(self.id_iter), position=(0, 0), first_name="D", last_name="D")

        self.candidates = [self.c3, self.c2, self.c1, self.c0]

    def test_plurality_simple(self):
        # Position n'affecte pas des résultats dans ce cas (candidates_ranked est définie manuellement)
        e0 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c2, self.c1, self.c0, self.c3])
        e1 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c2, self.c1, self.c0, self.c3])
        e2 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c0, self.c1, self.c3, self.c2])
        e3 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c3, self.c0, self.c1, self.c2])

        electors = [e0, e1, e2, e3]

        # Vérification d'un classement (égalités résolues par ordre alphabétique)
        ranking = [self.c2, self.c0, self.c3, self.c1]
        self.assertEqual(
            plurality.apply_plurality_simple(electors, self.candidates), ranking
        )

        # Vérification des scores
        self.assertEqual(self.c0.scores[PLURALITY_SIMPLE], 1)
        self.assertEqual(self.c1.scores[PLURALITY_SIMPLE], 0)
        self.assertEqual(self.c2.scores[PLURALITY_SIMPLE], 2)
        self.assertEqual(self.c3.scores[PLURALITY_SIMPLE], 1)

    def test_plurality_simple_tie_breaker(self):
        # Position n'affecte pas des résultats dans ce cas (candidates_ranked est définie manuellement)
        e0 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c2, self.c1, self.c3, self.c0])
        e1 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c2, self.c1, self.c3, self.c0])
        e2 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c0, self.c1, self.c3, self.c2])
        e3 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c3, self.c0, self.c1, self.c2])

        electors = [e0, e1, e2, e3]

        duels = set_duels_scores(electors, self.candidates)

        # Vérification d'un classement (égalités résolues par ordre alphabétique)
        self.assertEqual(
            plurality.apply_plurality_simple(electors, self.candidates, duels), [self.c2, self.c3, self.c0, self.c1]
        )

        # Vérification des scores
        self.assertEqual(self.c0.scores[PLURALITY_SIMPLE], 1)
        self.assertEqual(self.c1.scores[PLURALITY_SIMPLE], 0)
        self.assertEqual(self.c2.scores[PLURALITY_SIMPLE], 2)
        self.assertEqual(self.c3.scores[PLURALITY_SIMPLE], 1)

    def test_plurality_rounds(self):
        # Position n'affecte pas des résultats dans ce cas (candidates_ranked est définie manuellement)
        e0 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c2, self.c1, self.c0, self.c3])
        e1 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c2, self.c1, self.c0, self.c3])
        e2 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c0, self.c1, self.c3, self.c2])
        e3 = Elector(id=next(self.id_iter), position=(0, 0), candidates_ranked=[self.c3, self.c0, self.c1, self.c2])

        electors = [e0, e1, e2, e3]
        # Vérification d'un classement (égalités résolues par ordre alphabétique)
        self.assertEqual(
            plurality.apply_plurality_rounds(electors, self.candidates), [
                [self.c2, self.c0, self.c3, self.c1], [self.c0, self.c2]]
        )

        # Vérification des scores
        self.assertEqual(self.c0.scores[PLURALITY_2_ROUNDS], [1, 2])
        self.assertEqual(self.c1.scores[PLURALITY_2_ROUNDS], [0, 0])
        self.assertEqual(self.c2.scores[PLURALITY_2_ROUNDS], [2, 2])
        self.assertEqual(self.c3.scores[PLURALITY_2_ROUNDS], [1, 0])
