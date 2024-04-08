from .constants import CONDORCET_SIMPLE, CONDORCET_COPELAND, CONDORCET_SIMPSON
from .utls import Utls


def apply_condorcet_simple(electors, candidates, duels):

    Utls.init_scores(candidates, CONDORCET_SIMPLE, 0)
    for winner, _ in duels:
        winner.add_score(CONDORCET_SIMPLE, 1)
    return Utls.sort_cand_by_value(candidates, CONDORCET_SIMPLE)


def apply_condorcet_copeland(electors, candidates, duels):
    nb_electors = len(electors)
    Utls.init_scores(candidates, CONDORCET_COPELAND, 0)
    for (winner, loser), score in duels.items():
        if nb_electors % 2 == 0 and score == nb_electors // 2:
            winner.add_score(CONDORCET_COPELAND, 0.5)
            loser.add_score(CONDORCET_COPELAND, 0.5)
            continue
        winner.add_score(CONDORCET_COPELAND, 1)

    return Utls.sort_cand_by_value(candidates, CONDORCET_COPELAND)


def apply_condorcet_simpson(electors, candidates, duels):
    Utls.init_scores(candidates, CONDORCET_SIMPSON, 0)
    for (_, loser), score in duels.items():
        current_score = loser.scores[CONDORCET_SIMPSON]
        loser.init_score(CONDORCET_SIMPSON, max(current_score, score))
        current_score = loser.scores[CONDORCET_SIMPSON]

    return Utls.sort_cand_by_value(candidates, CONDORCET_SIMPSON, scores_asc=True)
