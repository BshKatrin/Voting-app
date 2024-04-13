from typing import List

from .constants import EXHAUSTIVE_BALLOT
from .utls import apply_voting_rule_rounds

from people import Candidate, Elector


def apply_exhaustive_ballot(electors: List[Elector], candidates: List[Candidate]) -> List[List[Candidate]]:
    """Applique la règle de vote *Éliminations successives*. Il n'est possible d'appliquer cette règle de vote que s'il existe au 
    moins 3 candidats.  
    Notons **N**: le nombre des candidats. Il existe au plus **N-1** tours (moins si un candidat a reçu la majorité
    absolue des votes).  
    Principe d'une règle de vote *Éliminations successives*:  
        - Chaque électeur doit placer tous les candidats selon ses préférences dans l'ordre décroissant.  
        - À chaque tour chaque candidat classé premier reçoit un point, tandis que les scores des autres candidats restent inchangés.  
        - Après chaque tour le candidat avec le score minimale est eliminé.


    Args:
        electors (List[people.elector.Elector]): Une liste de tous les électeurs participant à une élection.
            Leur liste `candidates_ranked` doit être remplie.
        candidates (List[people.candidate.Candidate]): Une liste de tous les candidats qui participent à une élection.

    Returns:
        List[people.candidate.Candidate]: Une liste des listes (classement dans l'ordre décroissant) des candidats par tour.
            La longueur de la liste correpond au nombre des tours effectués.
    """

    max_rounds = len(candidates) - 1
    elimination_index = -1  # i.e. éliminer tout le monde sauf le dernier
    return apply_voting_rule_rounds(electors, candidates, EXHAUSTIVE_BALLOT, max_rounds, elimination_index)
