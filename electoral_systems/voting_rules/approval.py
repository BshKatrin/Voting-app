from typing import List, Optional

from .constants import APPROVAL
from .utls import duels_type, init_scores, sort_cand_by_value

from people import Candidate, Elector


def apply_approval(electors: List[Elector], candidates: List[Candidate],
                   gap: float, duels: Optional[duels_type] = None) -> List[Candidate]:
    """Appliquer une règle du vote *Approbation*. Possible d'appliquer cette règle du vote s'il existe au moins 2 candidats.
    Principe d'une règle du vote *Approbation*:  
        - chaque électeur doit placer tous les candidats selon ses préférences dans l'ordre décroissant.
        - Chaque candidat reçoit un score en fonction de sa position dans le classement et en fonction d'un rayon d'une cercle 
        d'approbation. Le candidat classé premier reçoit un point à son score. Les autres candidats
        reçoivent un point ssi ils sont dand une cercle d'approbation d'un électeur. 
        Une cercle d'approbation d'un électeur est une cercle centré à la position d'un électeur et du rayon `gap` + distance entre
        la position du candidat classé premier et celle d'un électeur.

    Args:
        electors (List[people.elector.Elector]): Une liste de tous les électeurs participant dans une élection.
            Leur liste `candidates_ranked` doit être remplie.
        candidates (List[people.candidate.Candidate]): Une liste de tous les candidats qui participent dans une élection.
        duels (Utls.duels_type): Un dictionnaire qui associe à chaque duel des candidats (gagnant, perdant) le nombre des fois
        que le candidat-gagnant a battu le candidat-perdant. Default = `None`.
    Returns:
        List[people.candidate.Candidate]: Une liste des candidats triés dans l'ordre décroissant selon leurs dans
            la règle du vote *Approbation*.
    """
    init_scores(candidates, APPROVAL, 0)
    for elector in electors:
        dist_max = elector.dist_from_one_cand(
            elector.candidates_ranked[0]) + gap

        for candidate in elector.candidates_ranked:
            if elector.dist_from_one_cand(candidate) < dist_max:
                candidate.add_score(APPROVAL, elector.weight)
            else:
                break

    return sort_cand_by_value(candidates, APPROVAL, duels)
