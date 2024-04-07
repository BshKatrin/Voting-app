from .constants import EXHAUSTIVE_BALLOT
from .utls import Utls
from .condorcet import set_duels_scores


def apply_exhaustive_ballot(electors, candidates, duels):
    rounds = len(candidates) - 1  # amount of rounds to play (worst case scenario)
    len_electors = len(electors)
    # print(len_electors)
    # print(rounds)
    # Dans tous les cas il existe au moins 1 tour
    Utls.init_scores(candidates, EXHAUSTIVE_BALLOT, [0], True)
    # Play 1st round
    winners_backlog = [set_scores_round(electors, candidates, 0, duels)]
    current_round = 0
    # Continue until there is no candidate with majority
    # or there is only 1 candididate remains

    while current_round < rounds - 1 and (
        not Utls.has_majority(
            winners_backlog[current_round],
            len_electors,
            EXHAUSTIVE_BALLOT,
            current_round,
        )
    ):
        current_round += 1

        # Ajouter un slot pour round supplementaire
        for candidate in candidates:
            candidate.scores[EXHAUSTIVE_BALLOT].extend([0])

        candidates_curr_round = winners_backlog[current_round - 1][:-1]
        duels_curr_round = set_duels_scores(electors, candidates_curr_round)
        print(len(duels_curr_round))
        results = set_scores_round(
            electors, candidates_curr_round, current_round, duels_curr_round
        )
        winners_backlog.append(results)
    return winners_backlog


# Add scores to everyone
def set_scores_round(electors, remaining_candidates, round, duels):
    # Ajouter le score pour tout le monde
    if round == 0:
        for elector in electors:
            elector.candidates_ranked[0].add_score_round(
                EXHAUSTIVE_BALLOT, elector.weight, round
            )

    else:
        # Donner les scores pour les candidats restants
        for elector in electors:
            chosen_candidate = choose_next_candidate(elector, remaining_candidates)
            chosen_candidate.add_score_round(EXHAUSTIVE_BALLOT, elector.weight, round)
    return Utls.sort_cand_by_round(remaining_candidates, EXHAUSTIVE_BALLOT, round)


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
