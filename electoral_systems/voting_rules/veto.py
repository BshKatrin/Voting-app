from .constants import VETO
from .utls import init_scores, sort_cand_by_value


def apply_veto(electors, candidates):
    init_scores(candidates, VETO, 0)
    for elector in electors:
        i = 0
        for i in range(len(elector.candidates_ranked) - 1):
            # Ajouter +1 a chq candidat sauf le dernier
            elector.candidates_ranked[i].add_score(VETO, 1)
        # Ajouter rien au dernier candidat
        # i += 1
        # elector.candidates_ranked[i].add_score(VETO, 0)
    return sort_cand_by_value(candidates, VETO)
