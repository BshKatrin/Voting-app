from itertools import combinations

from .constants import CONDORCET_SIMPLE, CONDORCET_COPELAND, CONDORCET_SIMPSON
from .utls import init_scores, sort_cand_by_value


def apply_condorcet_simple(electors, candidates):
    for elector in electors:
        pairs = combinations(elector.candidates_ranked, 2)
        for fst, _ in pairs:
            fst.add_score(CONDORCET_SIMPLE, 1)
    return sort_cand_by_value(candidates, CONDORCET_SIMPLE)


def apply_condorcet_copeland(electors, candidates):
    # Initialisation des pairs des candidats
    # Chaque candidat va s'affronter chacun des autres -> pas des cas 'piege'
    duels = {comb: 0 for comb in combinations(candidates, 2)}
    # Comptage des win & loss
    for e in electors:
        pairs = combinations(e.candidates_ranked, 2)
        for fst, snd in pairs:
            if (fst, snd) in duels:
                duels[(fst, snd)] += 1
            elif (snd, fst) in duels:
                duels[(snd, fst)] -= 1
    # Ajouter des scores
    # Le code a ete simplifie un peu
    for (fst, snd), value in duels.items():
        if value > 0:
            fst.add_score(CONDORCET_COPELAND, 1)
            # pour eviter l'appel de method init_scores
            snd.add_score(CONDORCET_COPELAND, 0)
        elif value < 0:
            snd.add_score(CONDORCET_COPELAND, 1)
            # pour eviter l'appel de method init_scores
            fst.add_score(CONDORCET_COPELAND, 0)
        else:
            fst.add_score(CONDORCET_COPELAND, 0.5)
            snd.add_score(CONDORCET_COPELAND, 0.5)
    return sort_cand_by_value(candidates, CONDORCET_COPELAND)



def apply_condorcet_simpson(electors, candidates):
    # Compter tous les preferences dans les duels
    duels = dict()
    for comb in combinations(candidates, 2):
        duels[comb] = 0
        duels[comb[::-1]] = 0  # add reversed comb

    for elector in electors:
        pairs = combinations(elector.candidates_ranked, 2)
        for fst, snd in pairs:
            # if ... else pour protection
            # changer a try ... except ?
            if (fst, snd) in duels:
                duels[(fst, snd)] += 1
            else:
                duels[(snd, fst)] += 1

    init_scores(candidates, CONDORCET_SIMPSON, 0)

    for (_, snd), value in duels.items():
        snd.init_score(
            CONDORCET_SIMPSON,
            max(snd.scores[CONDORCET_SIMPSON], value),
        )

    return list(reversed(sort_cand_by_value(candidates, CONDORCET_SIMPSON)))