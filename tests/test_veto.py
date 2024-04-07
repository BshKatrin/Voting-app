import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from electoral_systems.voting_rules import veto
from people.elector import Elector
from people.candidate import Candidate


class TestVeto(unittest.TestCase):
    def test_veto(self):
        c0 = Candidate(first_name="A", last_name="B")
        c1 = Candidate(first_name="C", last_name="D")
        c2 = Candidate(first_name="E", last_name="F")
        c3 = Candidate(first_name="G", last_name="H")
        candidates = [c0, c1, c2, c3]

        e0 = Elector(candidates=candidates, candidates_ranked=[c0, c1, c2, c3])
        e1 = Elector(candidates=candidates, candidates_ranked=[c1, c0, c2, c3])
        e2 = Elector(candidates=candidates, candidates_ranked=[c3, c2, c1, c0])
        e3 = Elector(candidates=candidates, candidates_ranked=[c2, c0, c1, c3])
        e4 = Elector(candidates=candidates, candidates_ranked=[c2, c0, c3, c1])
        e5 = Elector(candidates=candidates, candidates_ranked=[c2, c0, c3, c1])
        electors = [e0, e1, e2, e3, e4, e5]

        self.assertEqual(veto.apply_veto(electors, candidates), [c2, c0, c1, c3])
