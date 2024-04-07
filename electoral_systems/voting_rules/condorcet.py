from itertools import combinations, permutations

from .constants import CONDORCET_SIMPLE, CONDORCET_COPELAND, CONDORCET_SIMPSON
from .utls import Utls


def apply_condorcet_simple(electors, candidates):
    duels = Utls.set_duels_scores(electors, candidates)
    Utls.init_scores(candidates, CONDORCET_SIMPLE, 0)
    for winner, _ in duels:
        winner.add_score(CONDORCET_SIMPLE, 1)
    return Utls.sort_cand_by_value(candidates, CONDORCET_SIMPLE)


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
    return Utls.sort_cand_by_value(candidates, CONDORCET_COPELAND)


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

    Utls.init_scores(candidates, CONDORCET_SIMPSON, 0)
    for (_, snd), value in duels.items():
        snd.init_score(
            CONDORCET_SIMPSON,
            max(snd.scores[CONDORCET_SIMPSON], value),
        )
    # Trier par l'ordre ascendant des scores des candidats, ensuite par leur nom
    return Utls.sort_cand_by_value(candidates, CONDORCET_SIMPSON, scores_asc=True)
