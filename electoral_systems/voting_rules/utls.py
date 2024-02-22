def init_scores(candidates, voting_system_name, new_score, list_type=False):
    """Initialiser le score des candidats dans le systeme du vote donne.
    Si list_type est True, initialiser les scores comme une liste"""
    for candidate in candidates:
        candidate.init_score(voting_system_name, new_score, list_type)


def sort_cand_by_value(candidates, voting_system_name):
    """Trier les candidats par leurs scores (ordre descendant),
    et ensuite par l'ordre alphabetique de leurs noms, prenoms"""
    lst = [
        (candidate, candidate.scores[voting_system_name]) for candidate in candidates
    ]
    return [c for (c, _) in sorted(lst, key=lambda e: (-e[1], e[0]))]


def sort_cand_by_round(candidates, voting_system_name, round):
    """Trier les candidats par leurs score (ordre descendant) dans le tour donne,
    et ensuite par l'ordre alphabetique de leurs noms, prenoms.
    Le tour commence a 0"""
    lst = [
        (candidate, candidate.scores[voting_system_name]) for candidate in candidates
    ]
    return [c for (c, _) in sorted(lst, key=lambda e: (-e[1][round], e[0]))]
