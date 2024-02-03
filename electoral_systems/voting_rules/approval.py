from .constants import APPROVAL
from .utls import sort_cand_by_value


# min_index commence par 1
# e.g. si min_index = 2 -> uniquement 2 premieres candidats recevront des points
def apply_approval(electors, candidates, min_index):
    for elector in electors:
        for i in range(min_index):
            elector.candidates_ranked[i].add_score(APPROVAL, 1)
    for i in range(min_index, len(candidates)):
        candidates[i].init_score(APPROVAL, 0)
    return sort_cand_by_value(candidates, APPROVAL)
