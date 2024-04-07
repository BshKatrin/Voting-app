from .constants import BORDA
from .utls import Utls


def apply_borda(electors, candidates, duels):
    nb_candidates = len(candidates)
    max_score = len(candidates) - 1
    Utls.init_scores(candidates, BORDA, 0)
    for elector in electors:
        for i in range(nb_candidates):
            elector.candidates_ranked[i].add_score(
                BORDA, (max_score - i) * elector.weight
            )
    return Utls.sort_cand_by_value(candidates, BORDA, duels)
