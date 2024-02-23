from .constants import EXHAUSTIVE_BALLOT
from .utls import init_scores, sort_cand_by_round


def apply_exhaustive_ballot(electors, candidates):
    rounds = len(candidates) - 1  # amount of rounds to play (worst case scenario)
    len_electors = len(electors)
    # Dans tous les cas il existe au moins 1 tour
    init_scores(candidates, EXHAUSTIVE_BALLOT, [0], True)
    # Play 1st round
    winners_backlog = [set_scores_round(electors, candidates, 0)]
    current_round = 0
    # Continue until there is no candidate with majority
    # or there is only 1 candididate remains

    while current_round < rounds - 1 and (
        not has_majority(winners_backlog[current_round], len_electors, current_round)
    ):
        current_round += 1

        # Ajouter un slot pour round supplementaire
        for candidate in candidates:
            candidate.scores[EXHAUSTIVE_BALLOT].extend([0])

        results = set_scores_round(
            electors, winners_backlog[current_round - 1][:-1], current_round
        )
        winners_backlog.append(results)
    return winners_backlog


# Add scores to everyone
def set_scores_round(electors, remaining_candidates, round):
    # Ajouter le score pour tout le monde
    if round == 0:
        for elector in electors:
            elector.candidates_ranked[0].add_score_round(EXHAUSTIVE_BALLOT, 1, round)

    else:
        # Donner les scores pour les candidats restants
        for elector in electors:
            chosen_candidate = choose_next_candidate(elector, remaining_candidates)
            chosen_candidate.add_score_round(EXHAUSTIVE_BALLOT, 1, round)
    return sort_cand_by_round(remaining_candidates, EXHAUSTIVE_BALLOT, round)


def choose_next_candidate(elector, remaining_candidates):
    remaining_candidates_set = set(remaining_candidates)
    index = 0
    current_candidate = elector.candidates_ranked[index]
    while index < len(remaining_candidates) and (
        current_candidate not in remaining_candidates_set
    ):
        index += 1
        current_candidate = elector.candidates_ranked[index]
    # Candidate does not exist,
    # if index == len(remaining_candidates):
    return current_candidate


# Verifier s'il existe un candidat qui a un majorite absolue des votes
def has_majority(candidates, len_electors, round):
    for candidate in candidates:
        if candidate.scores[EXHAUSTIVE_BALLOT][round] > len_electors / 2:
            return True
    return False
