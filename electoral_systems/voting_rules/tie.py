from itertools import combinations


class Tie:
    # Returns a sub list of indexes of candidates who are tied
    def get_ties(ranking, voting_rule):
        ties = []
        sublist = []
        prev_candidate = None

        for i, candidate in enumerate(ranking):
            if (
                prev_candidate
                and candidate.scores[voting_rule] == prev_candidate.scores[voting_rule]
            ):
                sublist.append(i)
            else:
                if len(sublist) > 1:
                    ties.append(sublist)
                sublist = [i]
            prev_candidate = candidate

        # In case, every candidate is tied
        if len(sublist) > 1:
            ties.append(sublist)

        return ties

    # Ties are resolved based on duels. Ranking is modified in place
    def resolve_ties(ranking, voting_rule, duels):
        print("Apply tie breaker")
        ties = Tie.get_ties(ranking, voting_rule)
        for tie in ties:
            for index1, index2 in combinations(tie, 2):
                candidate1, candidate2 = ranking[index1], ranking[index2]
                # candidate 1 is winner, do not rearrange
                if (candidate1, candidate2) in duels:
                    continue
                if (candidate2, candidate1) in duels:
                    ranking[index1], ranking[index2] = ranking[index2], ranking[index1]
