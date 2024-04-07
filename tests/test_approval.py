import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from electoral_systems.voting_rules import approval
from people.elector import Elector
from people.candidate import Candidate


class TestApproval(unittest.TestCase):
    def test_approval(self):
        c0 = Candidate(first_name="A", last_name="B", position=(0.6, 0.6))
        c1 = Candidate(first_name="C", last_name="D", position=(-0.6, -0.5))
        c2 = Candidate(first_name="E", last_name="F", position=(0, 0))
        c3 = Candidate(first_name="G", last_name="H", position=(1, 1))

        candidates = [c0, c1, c2, c3]

        e0 = Elector(candidates=candidates, position=(0.1, 0.1))
        e1 = Elector(candidates=candidates, position=(0.5, 0.5))
        e2 = Elector(candidates=candidates, position=(0.7, 0.8))
        e3 = Elector(candidates=candidates, position=(-0.5, -0.5))
        e4 = Elector(candidates=candidates, position=(1, 1))
        e5 = Elector(candidates=candidates, position=(0.8, 0.8))

        electors = [e0, e1, e2, e3, e4, e5]

        self.assertEqual(
            approval.apply_approval(electors, candidates), [c0, c3, c1, c2]
        )
