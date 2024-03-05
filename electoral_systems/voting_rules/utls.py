# Mettre les fonctions dans la classe Candidate?
def init_scores(candidates, voting_system_name, new_score, list_type=False):
    for candidate in candidates:
        candidate.init_score(voting_system_name, new_score, list_type)


# Trier des candidats selon leurs scores (int / float)
def sort_cand_by_value(candidates, voting_system_name):
    lst = [
        (candidate, candidate.scores[voting_system_name]) for candidate in candidates
    ]
    return [c for (c, _) in sorted(lst, key=lambda e: e[1], reverse=True)]


# Round commance a partir de 0
# Trier les candidats par rapport au round donne
def sort_cand_by_round(candidates, voting_system_name, round):
    lst = [
        (candidate, candidate.scores[voting_system_name]) for candidate in candidates
    ]
    return [c for (c, _) in sorted(lst, key=lambda e: e[1][round], reverse=True)]


# Verifier s'il existe un candidat qui a un majorite absolue des votes
def has_majority(candidates_sorted, len_electors, voting_system_name, round):
    return candidates_sorted[0].scores[voting_system_name][round] > len_electors / 2
