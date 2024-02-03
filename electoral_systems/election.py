from dataclasses import dataclass, field
from itertools import count
from typing import Dict, List

from people import Candidate
from people import Elector

import electoral_systems.voting_rules.constants as constants
from . import func_constants


@dataclass(kw_only=True)
class Election:
    id: int = field(default_factory=count().__next__)
    electors: List[Elector]
    candidates: List[Candidate]

    results: Dict[str, List[Candidate]] = field(default_factory=dict)

    def apply_voting_rule(self, voting_rule):
        self.results[voting_rule] = func_constants.VOTING_RULES_FUNC[voting_rule](
            self.electors, self.candidates
        )

    def choose_winner(self, voting_rule):
        if voting_rule not in self.results:
            self.apply_voting_rule(voting_rule)
        return self.results[voting_rule][0]
