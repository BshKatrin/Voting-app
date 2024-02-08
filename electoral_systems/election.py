from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List

from people import Candidate
from people import Elector

from electoral_systems.voting_rules.constants import *
from .func_constants import VOTING_RULES_FUNC
from .voting_rules.constants import *
from .singleton import Singleton
from people import Elector, Candidate


class Election(metaclass=Singleton):

    def __init__(self, electors=None, candidates=None):
        super().__init__()

        self.electors = deepcopy(electors) if electors else []
        self.candidates = deepcopy(candidates) if candidates else []
        self.results = dict()

    def add_elector(self, new_elector):
        self.electors.append(new_elector)

    def add_candidate(self, new_candidate):
        self.candidates.append(new_candidate)

    def has_electors_candidates(self):
        if not self.electors and not self.candidates:
            return False
        return True

    def apply_voting_rule(self, voting_rule):
        if not self.has_electors_candidates():
            pass
        self.results[voting_rule] = VOTING_RULES_FUNC[voting_rule](
            self.electors, self.candidates
        )

    def choose_winner(self, voting_rule):
        if voting_rule not in self.results:
            self.apply_voting_rule(voting_rule)
        if voting_rule == EXHAUSTIVE_BALLOT or voting_rule == PLURALITY_2_ROUNDS:
            return self.results[voting_rule][-1][0]
        return self.results[voting_rule][0]

    def init_results_keys(self, set_keys):
        for key in set_keys:
            self.results[key] = None
        print(self.results)

    def calculate_results(self):
        for voting_rule in self.results:
            self.apply_voting_rule(voting_rule)