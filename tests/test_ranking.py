import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from electoral_systems.utls import IdIterator
from people.elector import Elector
from people.candidate import Candidate


class TestRanking(unittest.TestCase):
    def test_rank_candidates(self):
        id_iter = IdIterator(0)
        c0 = Candidate(id=next(id_iter), position=(0.6, 0.5), first_name="A", last_name="A")
        c1 = Candidate(id=next(id_iter), position=(-0.6, 0.5), first_name="B", last_name="B")
        c2 = Candidate(id=next(id_iter), position=(0, 0), first_name="C", last_name="C")
        c3 = Candidate(id=next(id_iter), position=(0.9, -0.9), first_name="D", last_name="D")

        candidates = [c3, c2, c1, c0]

        e0 = Elector(id=next(id_iter), position=(0.1, 0.1))
        e1 = Elector(id=next(id_iter), position=(0.5, 0.5))
        e2 = Elector(id=next(id_iter), position=(-0.7, -0.8))
        e3 = Elector(id=next(id_iter), position=(-0.3, -0.3))
        e4 = Elector(id=next(id_iter), position=(0.9, 0.9))

        electors = [e0, e1, e2, e3, e4]
        for elector in electors:
            elector.rank_candidates(candidates)

        self.assertEqual(e0.candidates_ranked, [c2, c0, c1, c3])
        self.assertEqual(e1.candidates_ranked, [c0, c2, c1, c3])
        self.assertEqual(e2.candidates_ranked, [c2, c1, c3, c0])
        self.assertEqual(e3.candidates_ranked, [c2, c1, c0, c3])
        self.assertEqual(e4.candidates_ranked, [c0, c2, c1, c3])
