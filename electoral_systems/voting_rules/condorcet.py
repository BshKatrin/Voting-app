"""Ce module fournit des fonctions nécessaires pour les règles de vote Condorcet-cohérentes"""
from typing import List

from .constants import CONDORCET_SIMPLE, CONDORCET_COPELAND, CONDORCET_SIMPSON
from .utls import duels_type, init_scores, sort_cand_by_value

from people import Candidate, Elector


def apply_condorcet_simple(electors: List[Elector], candidates: List[Candidate], duels: duels_type) -> List[Candidate]:
    """Applique la régle de vote *Condorcet*. Il n'est possible d'appliquer cette règle de vote que s'il existe au moins 2 candidats.
    Principe d'une règle du vote *Condorcet*:  
        - Chaque électeur doit placer tous les candidats selon ses préférences dans l'ordre décroissant.  
        - Les duels entre les candidats sont calculés. Pour chaque duel, le gagnant reçoit un point, le perdant reçoit 0 points.    
        - Le gagnant de Condorcet est un candidat qui a battu tous les autres candidats en duel.  

    Args:
        electors (List[people.elector.Elector]): Une liste de tous les électeurs participant à une élection.
            Leur liste `candidates_ranked` doit être remplie.
        candidates (List[people.candidate.Candidate]): Une liste de tous les candidats qui participent à une élection.
        duels (electoral_systems.voting_rules.utls.duels_type): Un dictionnaire qui associe à chaque duel des candidats (gagnant, perdant) 
            le nombre des fois que le candidat-gagnant a battu le candidat-perdant.

    Returns:
        List[people.candidate.Candidate]: Une liste des candidats triés dans l'ordre décroissant selon leur score selon
            la règle de vote *Condorcet. Le premier candidat n'est pas forcément le gagnant.
    """
    
    init_scores(candidates, CONDORCET_SIMPLE, 0)
    for winner, _ in duels:
        winner.add_score(CONDORCET_SIMPLE, 1)
    return sort_cand_by_value(candidates, CONDORCET_SIMPLE, nb_electors=len(electors), duels=None)


def apply_condorcet_copeland(electors: List[Elector], candidates: List[Candidate], duels: duels_type) -> List[Candidate]:
    """Applique la régle de vote *Copeland*. Il n'est possible d'appliquer cette règle de vote que s'il existe au moins 2 candidats.
    Principe d'une règle de vote *Copeland*:  
        - Chaque électeur doit placer tous les candidats selon ses préférences dans l'ordre décroissant.  
        - Les duels entre les candidats sont calculés. Pour chaque duel, le gagnant reçoit un point, le perdant reçoit 0 points.
        Si c'est une égalité, chaque candidat du duel reçoit 0.5 points.  

    Args:
        electors (List[people.elector.Elector]): Une liste de tous les électeurs participant à une élection.
            Leur liste `candidates_ranked` doit être remplie.
        candidates (List[people.candidate.Candidate]): Une liste de tous les candidats qui participent à une élection.
        duels (electoral_systems.voting_rules.utls.duels_type): Un dictionnaire qui associe à chaque duel des candidats (gagnant, perdant) 
            le nombre des fois que le candidat-gagnant a battu le candidat-perdant.

    Returns:
        List[people.candidate.Candidate]: Une liste des candidats triés dans l'ordre décroissant selon leurs scores selon
            la règle de vote *Copeland*.
    """

    nb_electors = len(electors)  # Pour déterminer s'il existe une égalité
    init_scores(candidates, CONDORCET_COPELAND, 0)
    for (winner, loser), score in duels.items():
        if nb_electors % 2 == 0 and score == nb_electors // 2:
            winner.add_score(CONDORCET_COPELAND, 0.5)
            loser.add_score(CONDORCET_COPELAND, 0.5)
            continue
        winner.add_score(CONDORCET_COPELAND, 1)

    return sort_cand_by_value(candidates, CONDORCET_COPELAND, nb_electors=len(electors), duels=None)


def apply_condorcet_simpson(electors: List[Elector], candidates: List[Candidate], duels: duels_type) -> List[Candidate]:
    """Applique la régle de vote *Simpson*. Il n'est possible d'appliquer cette règle de vote que s'il existe au moins 2 candidats.
    Principe d'une règle du vote *Simpson*:  
        - Chaque électeur doit placer tous les candidats selon ses préférences dans l'ordre décroissant.  
        - Les duels entre les candidats sont calculés. Pour chaque duel, le gagnant reçoit 0 points, le perdant reçoit un point.  
        - Le gagnant est le candidat avec le minimum défaites.  

    Args:
        electors (List[people.elector.Elector]): Une liste de tous les électeurs participant à une élection.
            Leur liste `candidates_ranked` doit être remplie.
        candidates (List[people.candidate.Candidate]): Une liste de tous les candidats qui participent à une élection.
        duels (electoral_systems.voting_rules.utls.duels_type): Un dictionnaire qui associe à chaque duel des candidats (gagnant, perdant) 
            le nombre des fois que le candidat-gagnant a battu le candidat-perdant.

    Returns:
        List[people.candidate.Candidate]: Une liste des candidats triés dans l'ordre croissant selon leurs scores selon
            la règle de vote *Simpson*.
    """

    init_scores(candidates, CONDORCET_SIMPSON, 0)
    for (_, loser), score in duels.items():
        current_score = loser.scores[CONDORCET_SIMPSON]
        loser.init_score(CONDORCET_SIMPSON, max(current_score, score))
        current_score = loser.scores[CONDORCET_SIMPSON]

    return sort_cand_by_value(candidates, CONDORCET_SIMPSON, nb_electors=len(electors), duels=None, scores_asc=True)
