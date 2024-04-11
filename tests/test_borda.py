import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from electoral_systems.voting_rules import borda
from electoral_systems.voting_rules.constants import BORDA
from electoral_systems.voting_rules.utls import set_duels_scores
from electoral_systems.utls import IdIterator
from people.elector import Elector, Candidate


class TestBorda(unittest.TestCase):
    def test_borda(self):
        id_iter = IdIterator(0)
        p = (0, 0)
        # Position n'affecte pas des résultats dans ce cas (candidates_ranked sera définie manuellement)
        c0 = Candidate(id=next(id_iter), position=p, first_name="A", last_name="A")
        c1 = Candidate(id=next(id_iter), position=p, first_name="B", last_name="B")
        c2 = Candidate(id=next(id_iter), position=p, first_name="C", last_name="C")
        c3 = Candidate(id=next(id_iter), position=p, first_name="D", last_name="D")

        candidates = [c2, c1, c0, c3]
        electors = []

        for _ in range(2):
            new_elector = Elector(id=next(id_iter), position=p, candidates_ranked=[c2, c1, c0, c3])
            electors.append(new_elector)
        electors.append(Elector(id=next(id_iter), position=p, candidates_ranked=[c0, c1, c3, c2]))
        electors.append(Elector(id=next(id_iter), position=p, candidates_ranked=[c3, c0, c1, c2]))

        # Vérification d'un classement (égalités résolues par ordre alphabétique)
        self.assertEqual(borda.apply_borda(electors, candidates), [c0, c1, c2, c3])

        self.assertEqual(c0.scores[BORDA], 7)
        self.assertEqual(c1.scores[BORDA], 7)
        self.assertEqual(c2.scores[BORDA], 6)
        self.assertEqual(c3.scores[BORDA], 4)

        # Égalité par rapport aux duels, le classement ne doit pas changer
        duels = set_duels_scores(electors, candidates)
        self.assertEqual(borda.apply_borda(electors, candidates, duels), [c0, c1, c2, c3])
