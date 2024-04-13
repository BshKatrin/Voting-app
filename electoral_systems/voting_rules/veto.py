from typing import List, Optional

from .constants import VETO
from .utls import duels_type, init_scores, sort_cand_by_value

from people import Candidate, Elector


def apply_veto(electors: List[Elector], candidates: List[Candidate], duels: Optional[duels_type] = None) -> List[Candidate]:
    """Applique la règle de vote *Veto*. Il n'est possible d'appliquer cette règle du vote que s'il existe au moins 2 candidats.
    Principe d'une règle du vote *Veto*: 
        - chaque électeur doit placer tous les candidats selon ses préférences dans l'ordre décroissant.
        - pour chaque candidat, sauf le dernier dans ce classement, un point est attribué à son score.

    Args:
        electors (List[people.elector.Elector]): Une liste de tous les électeurs participant à une élection.
            Leur liste `candidates_ranked` doit être remplie.
        candidates (List[people.candidate.Candidate]): Une liste de tous les candidats qui participent à une élection.
        duels (Utls.duels_type): Un dictionnaire qui associe à chaque duel des candidats (gagnant, perdant) le nombre de fois
        que le candidat-gagnant a battu le candidat-perdant. Nécessaire uniquement s'il faut résoudre les égalités avec les duels.
        Default = `None`.
    Returns:
        List[people.candidate.Candidate]: Une liste des candidats triés dans l'ordre décroissant selon leur score selon la règle de vote *Veto*.
    """
    init_scores(candidates, VETO, 0)
    for elector in electors:
        i = 0
        for i in range(len(elector.candidates_ranked) - 1):
            # Ajouter +1 a chq candidat sauf le dernier
            elector.candidates_ranked[i].add_score(VETO, elector.weight)
        # Ajouter rien au dernier candidat
        # i += 1
        # elector.candidates_ranked[i].add_score(VETO, 0)
    return sort_cand_by_value(candidates, VETO, len(electors), duels)
