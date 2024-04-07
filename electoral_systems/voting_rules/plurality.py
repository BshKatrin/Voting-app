from copy import deepcopy

from .constants import PLURALITY_SIMPLE, PLURALITY_2_ROUNDS

from .utls import Utls
from .condorcet import set_duels_scores


def apply_plurality_simple(electors, candidates, duels=None):
    Utls.init_scores(candidates, PLURALITY_SIMPLE, 0)
    for elector in electors:
        elector.candidates_ranked[0].add_score(PLURALITY_SIMPLE, elector.weight)
    return Utls.sort_cand_by_value(candidates, PLURALITY_SIMPLE, duels)


# avant appel a la fonction : verifier qu'il existe AU MOINS 3 candidats
def apply_plurality_rounds(electors, candidates, duels=None):
    Utls.init_scores(candidates, PLURALITY_2_ROUNDS, [0], True)

    candidates_round_one = plurality_one_set_score(electors, candidates, duels)
    len_electors = len(electors)
    if Utls.has_majority(candidates_round_one, len_electors, PLURALITY_2_ROUNDS, 0):
        return [candidates_round_one]

    # Add new slot to every candidate
    for candidate in candidates:
        candidate.scores[PLURALITY_2_ROUNDS].extend([0])

    candidates_round_two = candidates_round_one[:2]
    duels_round_two = None
    if duels:
        set_duels_scores(electors, candidates_round_two)

    candidates_round_two = plurality_two_set_score(
        electors, candidates_round_two, duels_round_two
    )
    return [candidates_round_one, candidates_round_two]


def plurality_one_set_score(electors, candidates, duels):
    for elector in electors:
        # Ajouter +1 uniquement au premier candidat
        elector.candidates_ranked[0].add_score_round(
            PLURALITY_2_ROUNDS, elector.weight, 0
        )
    return Utls.sort_cand_by_round(candidates, PLURALITY_2_ROUNDS, 0, duels)


def plurality_two_set_score(electors, candidates, duels):
    for elector in electors:
        chosen_candidate = choose_next_candidate(elector, *candidates)
        chosen_candidate.add_score_round(PLURALITY_2_ROUNDS, elector.weight, 1)
    return Utls.sort_cand_by_round(candidates, PLURALITY_2_ROUNDS, 1, duels)


def choose_next_candidate(elector, cand1, cand2):
    index = 0
    current_candidate = elector.candidates_ranked[index]
    while current_candidate != cand1 and current_candidate != cand2:
        index += 1
        current_candidate = elector.candidates_ranked[index]
    return current_candidate
