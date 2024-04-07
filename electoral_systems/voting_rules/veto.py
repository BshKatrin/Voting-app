from .constants import VETO
from .utls import Utls


def apply_veto(electors, candidates, duels):
    Utls.init_scores(candidates, VETO, 0)
    for elector in electors:
        i = 0
        for i in range(len(elector.candidates_ranked) - 1):
            # Ajouter +1 a chq candidat sauf le dernier
            elector.candidates_ranked[i].add_score(VETO, elector.weight)
        # Ajouter rien au dernier candidat
        # i += 1
        # elector.candidates_ranked[i].add_score(VETO, 0)
    return Utls.sort_cand_by_value(candidates, VETO, duels)
