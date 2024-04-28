import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from people import Elector, Candidate
from electoral_systems.voting_rules import veto
from electoral_systems.voting_rules.constants import VETO
from electoral_systems.voting_rules.utls import set_duels_scores
from electoral_systems.utls import IdIterator

class TestVeto(unittest.TestCase):

    def test_veto(self):
        id_iter = IdIterator(0)

        # Position n'affecte pas des résultats dans ce cas (candidates_ranked sera définie manuellement)
        p = (0, 0)
        c0 = Candidate(id=next(id_iter), position=p, first_name="A", last_name="A")
        c1 = Candidate(id=next(id_iter), position=p, first_name="B", last_name="B")
        c2 = Candidate(id=next(id_iter), position=p, first_name="C", last_name="C")
        c3 = Candidate(id=next(id_iter), position=p, first_name="D", last_name="D")

        candidates = [c3, c1, c2, c0]

        e0 = Elector(id=next(id_iter), position=p, candidates_ranked=[c0, c1, c2, c3])
        e1 = Elector(id=next(id_iter), position=p, candidates_ranked=[c1, c0, c2, c3])
        e2 = Elector(id=next(id_iter), position=p, candidates_ranked=[c3, c2, c1, c0])
        e3 = Elector(id=next(id_iter), position=p, candidates_ranked=[c2, c0, c1, c3])
        e4 = Elector(id=next(id_iter), position=p, candidates_ranked=[c2, c0, c3, c1])
        e5 = Elector(id=next(id_iter), position=p, candidates_ranked=[c2, c0, c3, c1])
        electors = [e0, e1, e2, e3, e4, e5]

        # Vérification d'un classement (égalités résolues par ordre alphabétique)
        self.assertEqual(veto.apply_veto(electors, candidates), [c2, c0, c1, c3])

        # Vérification des scores
        self.assertEqual(c0.scores[VETO], 5)
        self.assertEqual(c1.scores[VETO], 4)
        self.assertEqual(c2.scores[VETO], 6)
        self.assertEqual(c3.scores[VETO], 3)

    def test_veto_tie_break(self):
        id_iter = IdIterator(0)
        p = (0, 0)
        # Position n'affecte pas des résultats dans ce cas (candidates_ranked sera définie manuellement)
        c0 = Candidate(id=next(id_iter), position=p, first_name="A", last_name="A")
        c1 = Candidate(id=next(id_iter), position=p, first_name="B", last_name="B")
        c2 = Candidate(id=next(id_iter), position=p, first_name="C", last_name="C")
        c3 = Candidate(id=next(id_iter), position=p, first_name="D", last_name="D")

        candidates = [c3, c1, c0, c2]

        e0 = Elector(id=next(id_iter), position=p, candidates_ranked=[c0, c1, c2, c3])
        e1 = Elector(id=next(id_iter), position=p, candidates_ranked=[c1, c0, c2, c3])
        e2 = Elector(id=next(id_iter), position=p, candidates_ranked=[c3, c2, c0, c1])
        e3 = Elector(id=next(id_iter), position=p, candidates_ranked=[c2, c0, c1, c3])
        e4 = Elector(id=next(id_iter), position=p, candidates_ranked=[c2, c0, c3, c1])
        e5 = Elector(id=next(id_iter), position=p, candidates_ranked=[c2, c0, c3, c1])
        electors = [e0, e1, e2, e3, e4, e5]

        # Vérification d'un classement (égalités résolues par duels)
        duels = set_duels_scores(electors, candidates)
        # Dans duels c1 et c3 sont égaux -> pas de changement
        # Dans duels c2 gagne contre c0 -> changement 
        self.assertEqual(veto.apply_veto(electors, candidates, duels), [c2, c0, c1, c3])

        # Vérification des scores
        self.assertEqual(c0.scores[VETO], 6) 
        self.assertEqual(c1.scores[VETO], 3)
        self.assertEqual(c2.scores[VETO], 6)
        self.assertEqual(c3.scores[VETO], 3)
