from itertools import combinations, permutations
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
            ranking = [c for (c, _) in sorted(lst, key=lambda e: (-e[1], e[0]))]
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
        duels = {perm: 0 for perm in permutations(candidates, 2)}

        for elector in electors:
            pairs = combinations(elector.candidates_ranked, 2)
            # combinations est inclus dans permutations -> pas de KeyError
            for fst, snd in pairs:
                if (fst, snd) in duels:
                    duels[(fst, snd)] += elector.weight
                elif (snd, fst) in duels:
                    duels[(snd, fst)] += elector.weight
        duels_simple = Utls._simplify_duels(duels)
        return duels_simple

    def _simplify_duels(duels):
        duels_simplified = dict()
        for c1, c2 in duels:
            if (c1, c2) in duels_simplified or (c2, c1) in duels_simplified:
                continue
            if duels[(c1, c2)] >= duels[(c2, c1)]:
                duels_simplified[(c1, c2)] = duels[(c1, c2)]
            else:
                duels_simplified[(c2, c1)] = duels[(c2, c1)]
        return duels_simplified
