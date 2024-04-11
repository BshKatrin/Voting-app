"""Un module qui fournit des fonctions auxiliaires nécessaires pour appliquer des règles du vote différentes.
De plus, il permet de factoriser des algorithmes pour des règles du vote à plusieurs tours."""

from itertools import combinations, permutations
from typing import Dict, List, Union, Optional

from .tie import resolve_ties
from people import Candidate, Elector

duels_type = Dict[tuple[Candidate, Candidate], int]


def init_scores(candidates: List[Candidate], voting_rule: str,
                new_score: Union[int, float, List[int]], list_type: Optional[bool] = False) -> None:
    """Initialiser les scores avec `new_score`de tous les candidats `candidates` dans une règle du vote `voting_rule`.

    Args:
        candidates (List[people.candidate.Candidate]): Une liste des candidats dont les scores il faut initialiser.
        voting_rule (str): Une constante associée à une règle du vote.
        new_score (Union[int, float, List[int]): Un nouveau score. Peut être une liste, dans ce cas l'initialisation passera
        par `deepcopy`.
        list_type (Optional[bool]): Un booléan pour indiquer si le type de `new_score` est une liste et s'il faut passer par `deepcopy`.
    """

    for candidate in candidates:
        candidate.init_score(voting_rule, new_score, list_type)


def sort_cand_by_value(candidates: List[Candidate], voting_rule: str, nb_electors: int,
                       duels: duels_type = None, scores_asc: bool = False) -> List[Candidate]:
    """Trier les candidats `candidates` selon leurs score dans une règle du vote `voting_rule`. Utiliser uniquement 
    pour les règles du vote à 1 tour ou Condorcet-cohérentes.
    S'il existe une égalité des scores trier par l'ordre alphabétique des leurs prénoms et noms.
    Si `duels` n'est pas `None`, résoudre une égalité avec les duels.

    Args:
        candidates (List[people.candidate.Candidate]): Une liste des candidats qu'il faut trier.
        voting_rule (str): Une constante associée à une règle du vote.
        nb_electors (int): Un nombre des électeurs qui participent dans une élection.
        duels (Utls.duels_type): Un dictionnaire qui associe à chaque duel des candidats (gagnant, perdant) le nombre des fois
        que le candidat-gagnant a battu le candidat-perdant. Nécessaire uniquement s'il faut résoudre les égalités avec les duels.
        Default = `None`.
        scores_asc (bool): Si True, trier par les scores de manière croissant, sinon de manière décroissant.

    Returns:
        List[people.candidate.Candidate]: Une liste des candidats triée et toutes les égalités résolues.
    """

    lst = [(candidate, candidate.scores[voting_rule])
           for candidate in candidates]

    if not scores_asc:
        ranking = [c for (c, _) in sorted(lst, key=lambda e: (-e[1], e[0]))]
    else:
        ranking = [c for (c, _) in sorted(lst, key=lambda e: (e[1], e[0]))]
    if duels:
        resolve_ties(ranking, nb_electors, voting_rule, duels)
    return ranking


def sort_cand_by_round(candidates: List[Candidate], voting_rule: str, round: int) -> List[Candidate]:
    """Trier les candidats `candidates` selon leurs score dans le tour `round` dans une règle du vote `voting_rule`. Utiliser uniquement 
    pour les règles du vote à plusieurs tours.
    S'il existe une égalité des scores trier par l'ordre alphabétique des leurs prénoms et noms.
    Si `duels` n'est pas `None`, résoudre une égalité avec les duels.

    Args:
        candidates (List[people.candidate.Candidate]): Une liste des candidats qu'il faut trier.
        voting_rule (str): Une constante associée à une règle du vote.
        round (int): Un tour d'une règle du vote (commence à partir de 0)

    Returns:
        List[people.candidate.Candidate]: Une liste des candidats triée et toutes les égalités résolues.
    """
    lst = [(candidate, candidate.scores[voting_rule][round]) for candidate in candidates]

    ranking = [c for (c, _) in sorted(lst, key=lambda e: (-e[1], e[0]))]
    return ranking


def _has_majority(candidates_sorted: List[Candidate], nb_electors: int, voting_rule: str, round: int) -> bool:
    """Vérifier si le candidat classé premier a la majorité absolue des votes dans une règle du vote `voting_rule`
    dans le tour `round`. Utiliser uniquement pour des règles du vote à plusieurs tours.

    Args:
        candidates_sorted (List[people.candidate.Candidate]): Une liste des candidats triée.
        nb_electors (int): Un nombre des électeurs qui participent dans une élection.
        voting_rule (str): Une constante associée à une règle du vote.
        round (int): Un tour d'une règle du vote  (commence à partir de 0).

    Returns:
        List[people.candidate.Candidate]: True si le premier candidat a la majorité des votes, sinon False.
    """
    return candidates_sorted[0].scores[voting_rule][round] > nb_electors / 2


def set_duels_scores(electors: List[Elector], candidates: List[Candidate]) -> duels_type:
    """Calculer les duels et des scores pour chaque duels. 

    Args:
        electors (List[people.elector.Elector]): Une liste des électeurs participant dans une élection.
        candidates (List[people.candidate.Candidate]): Une liste des candidats participant dans une élection.
    Returns:
        Utls.duels_type: Un dictionnaire dont les clés sont des paires des candidats (gagnant, perdant) et la
        valeur associé le nombre de fois que gagnant a battu perdant. Si (candidat1, candidat2) dans un dictionnaire,
        alors (candidat2, candidat1) ne sera pas présent. De plus, cela signifie que candidat1 a battu candidat2 plus de fois.
        Cf. _simplify_duels() <electoral_systems.voting_rules.utls._simplify_duels>
    """
    duels = {perm: 0 for perm in permutations(candidates, 2)}

    for elector in electors:
        pairs = combinations(elector.candidates_ranked, 2)
        # combinations est inclus dans permutations -> pas de KeyError
        for fst, snd in pairs:
            if (fst, snd) in duels:
                duels[(fst, snd)] += elector.weight
            elif (snd, fst) in duels:
                duels[(snd, fst)] += elector.weight
    duels_simple = _simplify_duels(duels)
    return duels_simple


def _simplify_duels(duels: duels_type) -> duels_type:
    """Éliminer les redondances d'un dictionnaire des duels, i.e. si candidat1 a battu candidat2 plus de fois,
    sauvegarder uniqument une clé (candidat1, candidat2) avec la valeur associé. 
    Cf. set_duels_scores() <electoral_systems.voting_rules.utls.set_duels_scores>

    Args:
        duels (Utls.duels_type): Un dictionnaire des duels avec les redondances, i.e. les paires 
        (candidat1, candidat2) et (candidat2, candidat1) sont présentes.

    Returns:
        Utls.duels_type: Un dictionnaire simplifié.
    """
    duels_simplified = dict()
    for c1, c2 in duels:
        if (c1, c2) in duels_simplified or (c2, c1) in duels_simplified:
            continue
        if duels[(c1, c2)] >= duels[(c2, c1)]:
            duels_simplified[(c1, c2)] = duels[(c1, c2)]
        else:
            duels_simplified[(c2, c1)] = duels[(c2, c1)]
    return duels_simplified


def apply_voting_rule_rounds(electors: List[Elector], candidates: List[Candidate],
                             voting_rule: str, max_rounds: int, elimination_index: int) -> List[List[Candidate]]:
    """
    Appliquer une régle du vote à plusieurs tours.

    Args:
        electors (List[people.elector.Elector]): Une liste des électeurs participant dans une élection.
        candidates (List[people.candidate.Candidate]): Une liste des candidats participant dans une élection.
        voting_rule (str): Une constante associée à une règle du vote.
        max_rounds (int): Le nombre des tours maximale qui peut exister dans une règle du vote.
        elimination_index (int): Une indice pour couper les candidats (utilisé pour couper la liste).

    Returns:
        List[List[people.candidate.Candidate]]: Une liste des listes (classement dans l'ordre décroissant) des candidats par tour.
            La longueur de la liste correpond au nombre des tours effectués (peut être inférieur à `max_rounds`)
    """
    init_scores(candidates, voting_rule, [0], True)
    # Tour 0, initialisation
    curr_round = 0
    winners_backlog = [_set_score_round(electors, candidates, voting_rule, curr_round)]
    majority_exists = _has_majority(winners_backlog[curr_round], len(electors), voting_rule, curr_round)

    while (curr_round < max_rounds - 1 and (not majority_exists)):
        curr_round += 1

        # Ajouter un slot pour un tour supplementaire
        for candidate in candidates:
            candidate.scores[voting_rule].extend([0])

        cands_curr_round = winners_backlog[curr_round - 1][:elimination_index]

        result_round = _set_score_round(electors, cands_curr_round, voting_rule, curr_round)

        winners_backlog.append(result_round)
        majority_exists = _has_majority(winners_backlog[curr_round], len(electors), voting_rule, curr_round)
    return winners_backlog


def _set_score_round(electors: List[Elector], remaining_candidates: List[Candidate],
                     voting_rule: str, round: int) -> List[Candidate]:
    """Ajouter le score pour chaque candidat qui encore participe dans une élection. Utiliser pour une règle du vote
    à plusieurs tours.

    Args:
        electors (List[people.elector.Elector]): Une liste des électeurs participant dans une élection.
        remaining_candidates (List[people.candidate.Candidate]): Une liste des candidats qui encore participent dans une élection.
        voting_rule (str): Une constante associée à une règle du vote.
        rount (int): Un tour pour lequell il faut ajouter le score.

    Returns
        List[people.candidate.Candidate]: Une liste (classement) des candidats triée dans l'ordre décroissant dans le tour `round`.
    """

    # Ajouter le score pour tout le monde
    if round == 0:
        for elector in electors:
            elector.candidates_ranked[0].add_score_round(voting_rule, elector.weight, round)

    else:
        # Donner les scores pour les candidats restants
        for elector in electors:
            chosen_candidate = _choose_next_cand(elector, remaining_candidates)
            chosen_candidate.add_score_round(voting_rule, elector.weight, round)
    return sort_cand_by_round(remaining_candidates, voting_rule, round)


def _choose_next_cand(elector: Elector, remaining_candidates: List[Candidate]) -> Candidate:
    """Choisir un candidat qui encore participe dans une élection selon les préférences d'un électeur.
    On choisit le premier candidat préféré d'un électeur parmi les candidats dans `remaining_candidates`.
    Utiliser pour une règle du vote à plusieurs tours.

    Args:
        elector (people.elector.Elector): Un électeur pour qui il faudra choisir un candidat restant.
        remaining_candidates (List[people.candidate.Candidate]): Une liste des candidats qui encore participent dans une élection.

    Returns:
        people.candidate.Candidate]: Un candidat choisi. Un électeur va voter pour lui.
    """
    remaining_candidates_set = set(remaining_candidates)
    index = 0
    current_candidate = elector.candidates_ranked[index]

    while index < len(remaining_candidates) and (
        current_candidate not in remaining_candidates_set
    ):
        index += 1
        current_candidate = elector.candidates_ranked[index]

    return current_candidate
