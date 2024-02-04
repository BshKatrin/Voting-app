from .constants import EXHAUSTIVE_BALLOT
from .utls import init_scores, sort_cand_by_round


def apply_exhaustive_ballot(electors, candidates):
    rounds = len(candidates) - 1  # amount of rounds to play (worst case scenario)
    len_electors = len(electors)

    # Dans tous les cas il existe plusieurs tours
    init_scores(candidates, EXHAUSTIVE_BALLOT, [0], True)
    # play 1st round
    winners_backlog = [set_scores_everyone(electors, candidates, 1)]
    current_round = 1
    # Continue until there is no candidate with majority (more than half)
    # or there is only 1 candididate remains
    while (current_round < rounds) or has_majority(
        winners_backlog[round - 1], len_electors
    ):
        current_round += 1
        winners_backlog.append(set_scores_everyone(electors, candidates, current_round))
        # electors = Elector.gen_rand_electors(len_electors, candidates)
    return winners_backlog


# Add scores to everyone
def set_scores_everyone(electors, candidates, round):
    for elector in electors:
        elector.candidates_ranked[0].add_score_round(EXHAUSTIVE_BALLOT, 1, round)
    return sort_cand_by_round(candidates, EXHAUSTIVE_BALLOT, round)


# Verifier s'il existe un candidat qui a un majorite absolue des votes
def has_majority(candidates, len_electors):
    for candidate in candidates:
        if candidate.scores[EXHAUSTIVE_BALLOT] > len_electors / 2:
            return True
    return False
