from typing import List, Optional

from .constants import BORDA
from .utls import duels_type, init_scores, sort_cand_by_value

from people import Candidate, Elector


def apply_borda(electors: List[Elector], candidates: List[Candidate], duels: duels_type = None) -> List[Candidate]:
    """Applique la règle de vote Borda. Il n'est possible d'appliquer cette règle de vote que s'il existe au moins 2 candidats. 
    Principe d'une règle de vote Borda:
    - Chaque électeur doit placer tous les candidats selon ses préférences dans l'ordre décroissant. 
    - Chaque candidat reçoit un score en fonction de sa position dans le classement. Notons $N$ le nombre des candidats. 
    Pour chaque classement, le candidat classé premier reçoit N-1 points, le deuxième N-2 points, et ainsi de suite, 
    jusqu'à ce que le dernier candidat reçoive 0 point.

    Args:
        electors (List[people.elector.Elector]): Une liste de tous les électeurs participant à une élection.
            Leur liste `candidates_ranked` doit être remplie.
        candidates (List[people.candidate.Candidate]): Une liste de tous les candidats qui participent à une élection.
        duels (Utls.duels_type): Un dictionnaire qui associe à chaque duel des candidats (gagnant, perdant) le nombre des fois
        que le candidat-gagnant a battu le candidat-perdant. Default = `None`.
    Returns:
        List[people.candidate.Candidate]: Une liste des candidats triés dans l'ordre décroissant selon leurs score selon la règle de vote *Borda*.
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
