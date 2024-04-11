"""Ce module fournit des fonctions nécessaires pour des règles du vote du type Pluralité"""

from typing import List, Optional
from .constants import PLURALITY_SIMPLE, PLURALITY_2_ROUNDS

from .utls import duels_type, init_scores, sort_cand_by_value, apply_voting_rule_rounds

from people import Candidate, Elector


def apply_plurality_simple(electors: List[Elector], candidates: List[Candidate],
                           duels: Optional[duels_type] = None) -> List[Candidate]:
    """Appliquer une règle du vote *Pluralité à 1 tour*. Possible d'appliquer cette règle du vote s'il existe au moins 2 candidats.
    Principe d'une règle du vote *Pluralité à 1 tour*: 
        - Chaque électeur doit placer tous les candidats selon ses préférences dans l'ordre décroissant.
        - Chaque candidat classé premier un point est attribué à son score. Les scores des autres candidats ne changent pas.


    Args:
        electors (List[people.elector.Elector]): Une liste de tous les électeurs participant dans une élection.
            Leur liste `candidates_ranked` doit être remplie.
        candidates (List[people.candidate.Candidate]): Une liste de tous les candidats qui participent dans une élection.
        duels (Utls.duels_type): Un dictionnaire qui associe à chaque duel des candidats (gagnant, perdant) le nombre des fois
        que le candidat-gagnant a battu le candidat-perdant. Default = `None`.
    Returns:
        List[people.candidate.Candidate]:  Une liste des candidats triés dans l'ordre décroissant selon leurs scores dans
            la règle du vote *Pluralité à 1 tour*
    """
    init_scores(candidates, PLURALITY_SIMPLE, 0)
    for elector in electors:
        elector.candidates_ranked[0].add_score(
            PLURALITY_SIMPLE, elector.weight)
    return sort_cand_by_value(candidates, PLURALITY_SIMPLE, len(electors), duels)


def apply_plurality_rounds(electors: List[Elector], candidates: List[Candidate]) -> List[List[Candidate]]:
    """Appliquer une règle du vote *Pluralité à 2 tours*. Possible d'appliquer cette règle du vote s'il existe au moins 3 candidats.
      Principe d'une règle du vote *Pluralité à 2 tours*: 
        - Chaque électeur doit placer tous les candidats selon ses préférences dans l'ordre décroissant.
        - Tour 1 : Chaque candidat classé premier reçoit un point, tandis que les scores des autres candidats restent inchangés.
        - Tour 2: Ce tour commence si aucun candidat n'obtient la majorité absolue des votes au premier tour.
        Dans ce cas, les deux candidats ayant les scores les plus élevés passent au deuxième tour, tandis que les autres sont éliminés.
        Les électeurs classent alors ces deux candidats selon leurs préférences, en ordre décroissant.
        Comme au premier tour, le candidat classé premier reçoit 1 point, et le deuxième 0 point.


    Args:
        electors (List[people.elector.Elector]): Une liste de tous les électeurs participant dans une élection.
            Leur liste `candidates_ranked` doit être remplie.
        candidates (List[people.candidate.Candidate]): Une liste de tous les candidats qui participent dans une élection.

    Returns:
        List[people.candidate.Candidate]: Une liste des listes (classement dans l'ordre décroissant) des candidats par tour. La longueur de la liste correpond
        au nombre des tours effectués.
    """

    max_rounds = 2
    elimination_index = 2  # i.e. on ne considère que 2 premiers candidats dans le 2ème tour
    res = apply_voting_rule_rounds(
        electors, candidates, PLURALITY_2_ROUNDS, max_rounds, elimination_index)
    return res
