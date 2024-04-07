import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from electoral_systems.voting_rules import plurality
from people.elector import Elector
from people.candidate import Candidate


class TestPlurality(unittest.TestCase):

    def test_plurality_simple(self):
        c0 = Candidate(first_name="A", last_name="B", position=(0.6, 0.5))
        c1 = Candidate(first_name="C", last_name="D", position=(-0.6, -0.5))
        c2 = Candidate(first_name="E", last_name="F", position=(0, 0))

        candidates = [c0, c1, c2]

        e0 = Elector(candidates=candidates, position=(0.1, 0.1))  # vote pour c3
        e1 = Elector(candidates=candidates, position=(0.5, 0.5))  # vote pour c1
        e2 = Elector(candidates=candidates, position=(0.7, 0.8))  # vote pour c1
        e3 = Elector(candidates=candidates, position=(-0.5, -0.5))  # vote pour c2
        e4 = Elector(candidates=candidates, position=(1, 1))  # vote pour c1

        electors = [e0, e1, e2, e3, e4]
        self.assertEqual(
            plurality.apply_plurality_simple(electors, candidates), [c0, c1, c2]
        )

    def test_plurality_rounds(self):
        c0 = Candidate(first_name="A", last_name="B", position=(0.6, 0.5))
        c1 = Candidate(first_name="C", last_name="D", position=(-0.6, -0.5))
        c2 = Candidate(first_name="E", last_name="F", position=(0, 0))

        candidates = [c0, c1, c2]

        e0 = Elector(candidates=candidates, position=(0.1, 0.1))  # vote pour c3
        e1 = Elector(candidates=candidates, position=(0.5, 0.5))  # vote pour c1
        e2 = Elector(candidates=candidates, position=(0.7, 0.8))  # vote pour c1
        e3 = Elector(candidates=candidates, position=(-0.5, -0.5))  # vote pour c2
        e4 = Elector(candidates=candidates, position=(1, 1))  # vote pour c1

        electors = [e0, e1, e2, e3, e4]

        self.assertEqual(
            plurality.apply_plurality_rounds(electors, candidates),
            ([c0, c1, c2], [c0, c1]),
        )
        # c2 se fait eliminer et son votant vote pour c0
