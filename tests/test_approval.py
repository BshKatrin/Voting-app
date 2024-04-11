import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from electoral_systems.voting_rules import approval
from electoral_systems.voting_rules.constants import APPROVAL
from electoral_systems.utls import IdIterator
from people.elector import Elector, Candidate


class TestApproval(unittest.TestCase):
    def test_approval(self):
        id_iter = IdIterator(0)
        c0 = Candidate(id=next(id_iter), first_name="A", last_name="A", position=(0.6, 0.6))
        c1 = Candidate(id=next(id_iter), first_name="B", last_name="B", position=(-0.6, -0.5))
        c2 = Candidate(id=next(id_iter), first_name="C", last_name="C", position=(0, 0))
        c3 = Candidate(id=next(id_iter), first_name="d", last_name="d", position=(1, 1))

        candidates = [c3, c1, c0, c2]

        e0 = Elector(id=next(id_iter), position=(0.1, 0.1))
        e1 = Elector(id=next(id_iter), position=(0.5, 0.5))
        e2 = Elector(id=next(id_iter), position=(0.7, 0.8))
        e3 = Elector(id=next(id_iter), position=(-0.5, -0.5))
        e4 = Elector(id=next(id_iter), position=(1, 1))
        e5 = Elector(id=next(id_iter), position=(0.8, 0.8))

        electors = [e0, e1, e2, e3, e4, e5]

        for elector in electors:
            elector.rank_candidates(candidates)

        self.assertEqual(
            approval.apply_approval(electors, candidates, 0.3), [c0, c3, c1, c2]
        )

        self.assertEqual(c0.scores[APPROVAL], 3)
        self.assertEqual(c1.scores[APPROVAL], 1)
        self.assertEqual(c2.scores[APPROVAL], 1)
        self.assertEqual(c3.scores[APPROVAL], 3)
