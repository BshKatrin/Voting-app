from .constants import BORDA
from .utls import sort_cand_by_value, init_scores


def apply_borda(electors, candidates):
    nb_candidates = len(candidates)
    max_score = len(candidates) - 1
    init_scores(candidates, BORDA, 0)
    for elector in electors:
        for i in range(nb_candidates):
            elector.candidates_ranked[i].add_score(BORDA, max_score - i)
    return sort_cand_by_value(candidates, BORDA)
