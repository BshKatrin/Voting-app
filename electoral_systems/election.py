from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List

from people import Candidate
from people import Elector

import electoral_systems.voting_rules.constants as constants
from . import func_constants
from .singleton import Singleton

from people import Elector, Candidate


class Election(Singleton):

    def __init__(self, electors=[], candidates=[]):
        super().__init__()

        self.electors = deepcopy(electors)
        self.candidates = deepcopy(candidates)
        self.results = dict()

    def add_elector(self, new_elector):
        self.electors.append(new_elector)

    def add_candidate(self, new_candidate):
        self.candidates.append(new_candidate)

    def has_electors_candidtates(self):
        if not self.electors and not self.candidates:
            return False
        return True

    def apply_voting_rule(self, voting_rule):
        if not self.has_electors_candidtates():
            pass
        self.results[voting_rule] = func_constants.VOTING_RULES_FUNC[voting_rule](
            self.electors, self.candidates
        )

    def choose_winner(self, voting_rule):
        if voting_rule not in self.results:
            self.apply_voting_rule(voting_rule)
        return self.results[voting_rule][0]
