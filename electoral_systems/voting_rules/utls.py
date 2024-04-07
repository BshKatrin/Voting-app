from itertools import combinations
from .tie import Tie


class Utls:
    # Mettre les fonctions dans la classe Candidate?
    def init_scores(candidates, voting_rule, new_score, list_type=False):
        for candidate in candidates:
            candidate.init_score(voting_rule, new_score, list_type)

    # Trier des candidats selon leurs scores (int / float)
    def sort_cand_by_value(candidates, voting_rule, duels=None, scores_asc=False):

        lst = [(candidate, candidate.scores[voting_rule]) for candidate in candidates]

        if not scores_asc:
            ranking = [c for (c, _) in sorted(lst, key=lambda e: e[1], reverse=True)]
        else:
            ranking = [c for (c, _) in sorted(lst, key=lambda e: (e[1], e[0]))]

        if duels:
            Tie.resolve_ties(ranking, voting_rule, duels)
        return ranking

    # Round commance a partir de 0
    # Trier les candidats par rapport au round donne
    def sort_cand_by_round(candidates, voting_rule, round, duels=None):
        lst = [(candidate, candidate.scores[voting_rule]) for candidate in candidates]
        ranking = [c for (c, _) in sorted(lst, key=lambda e: e[1][round], reverse=True)]
        if duels:
            Tie.resolve_ties(ranking, voting_rule, duels)
        return ranking

    # Verifier s'il existe un candidat qui a un majorite absolue des votes
    def has_majority(candidates_sorted, len_electors, voting_rule, round):
        return candidates_sorted[0].scores[voting_rule][round] > len_electors / 2

    def set_duels_scores(electors, candidates):
        pairs = {comb: 0 for comb in combinations(candidates, 2)}
        nb_electors = 0
        for elector in electors:
            nb_electors += 1
            pairs_elector = {
                comb: 0 for comb in combinations(elector.candidates_ranked, 2)
            }
            for fst, snd in pairs_elector:
                if (fst, snd) in pairs:
                    pairs[(fst, snd)] += elector.weight
                elif (snd, fst) in pairs:
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
