import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from electoral_systems.voting_rules import exhaustive_ballot
from electoral_systems.voting_rules.constants import EXHAUSTIVE_BALLOT
from electoral_systems.utls.id_iterator import IdIterator
from people.elector import Elector, Candidate


class TestExhaustiveBallot(unittest.TestCase):

    def test_exhaustive_ballot(self):
        id_iter = IdIterator(0)

        c0 = Candidate(id=next(id_iter), position=(0, 0), first_name="A", last_name="A")
        c1 = Candidate(id=next(id_iter), position=(0, 0), first_name="B", last_name="B")
        c2 = Candidate(id=next(id_iter), position=(0, 0), first_name="C", last_name="C")
        c3 = Candidate(id=next(id_iter), position=(0, 0), first_name="D", last_name="D")
        candidates = [c2, c1, c0, c3]

        electors = []
        for _ in range(3):
            new_elector = Elector(id=next(id_iter), position=(0, 0), candidates_ranked=[c0, c3, c1, c2])
            electors.append(new_elector)

        for _ in range(4):
            new_elector = Elector(id=next(id_iter), position=(0, 0), candidates_ranked=[c1, c3, c0, c2])
            electors.append(new_elector)

        for _ in range(3):
            new_elector = Elector(id=next(id_iter), position=(0, 0), candidates_ranked=[c2, c3, c0, c1])
            electors.append(new_elector)

        for _ in range(2):
            new_elector = Elector(id=next(id_iter), position=(0, 0), candidates_ranked=[c3, c2, c1, c0])
            electors.append(new_elector)

        # Vérification d'un classement (égalités résolues par ordre alphabétique)
        self.assertEqual(
            exhaustive_ballot.apply_exhaustive_ballot(electors, candidates),
            [[c1, c0, c2, c3], [c2, c1, c0], [c1, c2]],
        )

        # Vérification des scores
        self.assertEqual(c0.scores[EXHAUSTIVE_BALLOT], [3, 3, 0])
        self.assertEqual(c1.scores[EXHAUSTIVE_BALLOT], [4, 4, 7])
        self.assertEqual(c2.scores[EXHAUSTIVE_BALLOT], [3, 5, 5])
        self.assertEqual(c3.scores[EXHAUSTIVE_BALLOT], [2, 0, 0])
