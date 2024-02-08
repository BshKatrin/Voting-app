from .constants import BORDA
from .utls import sort_cand_by_value


def apply_borda(electors, candidates):
    max_score = len(candidates) - 1
    for elector in electors:
        for i in range(len(candidates)):
            elector.candidates_ranked[i].add_score(BORDA, max_score - i)
    return sort_cand_by_value(candidates, BORDA)
