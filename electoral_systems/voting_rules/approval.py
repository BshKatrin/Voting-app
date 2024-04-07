from .constants import APPROVAL
from .utls import Utls

"""
apply_approval([electors],[candidates])->[candidates]
les votes des electeurs sont determinés par leur distance en fonction des candidats
(chaque electeurs peut donc voter pour un nombre de candidats différents >=1)
"""


def apply_approval(electors, candidates, gap, duels):
    Utls.init_scores(candidates, APPROVAL, 0)
    for elector in electors:
        dist_max = elector.dist_from_one_cand(elector.candidates_ranked[0]) + gap
        for candidate in elector.candidates_ranked:
            if elector.dist_from_one_cand(candidate) < dist_max:
                candidate.add_score(APPROVAL, elector.weight)
            else:
                candidate.add_score(APPROVAL, 0)
                break
    return Utls.sort_cand_by_value(candidates, APPROVAL, duels)
