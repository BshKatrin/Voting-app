from .constants import PLURALITY_SIMPLE, PLURALITY_2_ROUNDS

from .utls import init_scores, sort_cand_by_value, sort_cand_by_round

from people.elector import Elector


def apply_plurality_simple(electors, candidates):
    init_scores(candidates, PLURALITY_SIMPLE, 0)
    for elector in electors:
        elector.candidates_ranked[0].add_score(PLURALITY_SIMPLE, 1)
    return sort_cand_by_value(candidates, PLURALITY_SIMPLE)


# avant appel a la fonction : verifier qu'il existe AU MOINS 3 candidats
def apply_plurality_rounds(electors, candidates):
    init_scores(candidates, PLURALITY_2_ROUNDS, [0, 0], True)

    candidates_round_one = plurality_one_set_score(electors, candidates)
    candidates_round_two = candidates_round_one[:2]
    
    candidates_round_two = plurality_two_set_score(electors, candidates_round_two)

    return candidates_round_one, candidates_round_two


def plurality_one_set_score(electors, candidates):
    for elector in electors:
        # Ajouter +1 uniquement au premier candidat
        elector.candidates_ranked[0].add_score_round(PLURALITY_2_ROUNDS, 1, 1)
    return sort_cand_by_round(candidates, PLURALITY_2_ROUNDS, 1)


def plurality_two_set_score(electors, candidates):
    for elector in electors:
        chosen_candidate = choose_next_candidate(elector, *candidates)
        chosen_candidate.add_score_round(PLURALITY_2_ROUNDS, 1, 2)
    return sort_cand_by_round(candidates, PLURALITY_2_ROUNDS, 2)


def choose_next_candidate(elector, cand1, cand2):
    index = 0
    current_candidate = elector.candidates_ranked[index]
    while (current_candidate != cand1 and current_candidate != cand2):
        index += 1
        current_candidate = elector.candidates_ranked[index]
    return current_candidate
