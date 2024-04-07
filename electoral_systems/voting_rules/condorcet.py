from itertools import combinations, permutations

from .constants import CONDORCET_SIMPLE, CONDORCET_COPELAND, CONDORCET_SIMPSON
from .utls import init_scores, sort_cand_by_value


# Utile pour les graphes et pour le condorcet simple
# i.e. pour determiner s'il existe un gagnant ou pas
def set_duels_scores(electors, candidates):
    print("Setting duels")
    pairs = {comb: 0 for comb in combinations(candidates, 2)}
    nb_electors = 0
    for elector in electors:
        nb_electors += 1
        pairs_elector = {comb: 0 for comb in combinations(elector.candidates_ranked, 2)}
        for fst, snd in pairs_elector:
            if (fst, snd) in pairs:
                pairs[(fst, snd)] += elector.weight
            else:
                pairs[(snd, fst)] -= elector.weight

    duels = dict()
    for pair, score in pairs.items():
        if score < 0:
            duels[pair[::-1]] = nb_electors + score
        elif score > 0:
            duels[pair] = nb_electors - score
        else:
            duels[pair] = 0
    return duels


def apply_condorcet_simple(electors, candidates):
    duels = set_duels_scores(electors, candidates)
    init_scores(candidates, CONDORCET_SIMPLE, 0)
    for winner, _ in duels:
        winner.add_score(CONDORCET_SIMPLE, 1)
    return sort_cand_by_value(candidates, CONDORCET_SIMPLE)


def apply_condorcet_copeland(electors, candidates):
    # Initialisation des pairs des candidats
    # Chaque candidat va s'affronter chacun des autres -> pas des cas 'piege'
    duels = {comb: 0 for comb in combinations(candidates, 2)}
    # Comptage des win & loss
    for elector in electors:
        pairs = combinations(elector.candidates_ranked, 2)
        for fst, snd in pairs:
            if (fst, snd) in duels:
                duels[(fst, snd)] += elector.weight
            elif (snd, fst) in duels:
                duels[(snd, fst)] -= elector.weight

    # Ajouter des scores
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
    duels = {perm: 0 for perm in permutations(candidates, 2)}

    for elector in electors:
        pairs = combinations(elector.candidates_ranked, 2)
        # combinations est inclus dans permutations -> pas de KeyError
        for fst, snd in pairs:
            if (fst, snd) in duels:
                duels[(fst, snd)] += elector.weight
            else:
                duels[(snd, fst)] += elector.weight

    init_scores(candidates, CONDORCET_SIMPSON, 0)
    for (_, snd), value in duels.items():
        snd.init_score(
            CONDORCET_SIMPSON,
            max(snd.scores[CONDORCET_SIMPSON], value),
        )
    # Trier par l'ordre ascendant des scores des candidats, ensuite par leur nom
    return sort_cand_by_value(candidates, CONDORCET_SIMPSON, scores_asc=True)
