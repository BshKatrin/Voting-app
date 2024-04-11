"""Un module fournit la fonctionnalité pour résoudre des égalités en fonction des duels entre les candidats."""

from itertools import combinations
from typing import List, Dict

from people import Candidate

duels_type = Dict[tuple[Candidate, Candidate], int]


def get_ties(ranking: List[Candidate], voting_rule: str) -> List[List[int]]:
    """Trouver toutes les égalités entre les candidats.

    Args:
        ranking (List[Candidate]): Un classement des candidats dans une règle du vote `voting_rule` selon leurs scores.
        voting_rule (str): Une constante associée à une règle du vote.

    Returns:
        List[List[int)]]: Une liste dont chaque élément est une liste des indices des candidats dans `ranking`
        qui ont le même score.
    """

    ties = []
    sublist = []
    prev_candidate = None

    for i, candidate in enumerate(ranking):
        if (prev_candidate and candidate.scores[voting_rule] == prev_candidate.scores[voting_rule]):
            sublist.append(i)
        else:
            if len(sublist) > 1:
                ties.append(sublist)
            sublist = [i]
        prev_candidate = candidate

    # Au cas où tous les candidats seraient à égalité
    if len(sublist) > 1:
        ties.append(sublist)

    return ties


def resolve_ties(ranking: List[Candidate], voting_rule: str, duels: duels_type) -> None:
    """Résoudre toutes lse égalités entre les candidats selon les duels. Le gagnant d'une égalité est un candidat
    qui a gagné le duel. S'il existe plusieurs candidats avec le même score, ils sont comparés 2 à 2. Un classement 
    `ranking` est modifié sur place.

    Args:
        ranking (List[Candidate]): Un classement des candidats dans une règle du vote `voting_rule` selon leurs scores.
        voting_rule (str): Une constante associée à une règle du vote.
        duels (Utls.duels_type): Un dictionnaire qui associe à chaque duel des candidats (gagnant, perdant) le nombre des fois
            que le candidat-gagnant a battu le candidat-perdant. C'est une base pour résoudre des égalités.
    """
    ties = get_ties(ranking, voting_rule)
    for tie in ties:
        for index1, index2 in combinations(tie, 2):
            candidate1, candidate2 = ranking[index1], ranking[index2]
            # candidate 1 is winner, do not rearrange
            if (candidate1, candidate2) in duels:
                continue
            if (candidate2, candidate1) in duels:
                ranking[index1], ranking[index2] = ranking[index2], ranking[index1]
