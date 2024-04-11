from typing import List, Optional

from .constants import BORDA
from .utls import duels_type, init_scores, sort_cand_by_value

from people import Candidate, Elector


def apply_borda(electors: List[Elector], candidates: List[Candidate], duels: duels_type = None) -> List[Candidate]:
    """Appliquer une règle du vote *Borda*.  Possible d'appliquer cette règle du vote s'il existe au moins 2 candidats.
    Principe d'une règle du vote *Borda*:  
        - chaque électeur doit placer tous les candidats selon ses préférences dans l'ordre décroissant.
        - Chaque candidat reçoit un score en fonction de sa position dans le classement.
        Notons $N$ le nombre des candidats. Pour chaque classement, le candidat classé premier reçoit N-1 points,
        le deuxième N-2 points, et ainsi de suite, jusqu'à ce que le dernier candidat reçoive 0 point.
        reçoit 0 points.        

    Args:
        electors (List[people.elector.Elector]): Une liste de tous les électeurs participant dans une élection.
            Leur liste `candidates_ranked` doit être remplie.
        candidates (List[people.candidate.Candidate]): Une liste de tous les candidats qui participent dans une élection.
        duels (Utls.duels_type): Un dictionnaire qui associe à chaque duel des candidats (gagnant, perdant) le nombre des fois
        que le candidat-gagnant a battu le candidat-perdant. Default = `None`.
    Returns:
        List[people.candidate.Candidate]: Une liste des candidats triés dans l'ordre décroissant selon leurs dans la règle du vote *Borda*.
    """
    nb_candidates = len(candidates)
    max_score = len(candidates) - 1
    init_scores(candidates, BORDA, 0)
    for elector in electors:
        for i in range(nb_candidates):
            elector.candidates_ranked[i].add_score(
                BORDA, (max_score - i) * elector.weight
            )
    return sort_cand_by_value(candidates, BORDA, len(electors), duels)
