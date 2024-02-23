from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List

from people import Candidate
from people import Elector

from electoral_systems.voting_rules.constants import *
from .func_constants import VOTING_RULES_FUNC

from .voting_rules.constants import *
from .voting_rules.condorcet import set_duels_scores

from .singleton import Singleton
from people import Elector, Candidate


class Election(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.electors = []
        self.candidates = []
        self.electors_positions = []

        self.results = dict()
        self.condorcet_graph_info = dict()

    def add_elector(self, new_elector):
        self.electors.append(new_elector)

    def add_candidate(self, new_candidate):
        self.candidates.append(new_candidate)

    def add_electors_position(self, position):
        self.electors_positions.append(position)

    def has_electors_candidates(self):
        if not self.electors and not self.candidates:
            return False
        return True

    def apply_voting_rule(self, voting_rule):
        if not self.has_electors_candidates():
            pass

        if voting_rule in {CONDORCET_SIMPLE, CONDORCET_COPELAND, CONDORCET_SIMPSON}:
            self.condorcet_graph_info = set_duels_scores(self.electors, self.candidates)

        self.results[voting_rule] = VOTING_RULES_FUNC[voting_rule](
            self.electors, self.candidates
        )

    def choose_winner(self, voting_rule):
        if voting_rule not in self.results:
            self.apply_voting_rule(voting_rule)
        if voting_rule == EXHAUSTIVE_BALLOT or voting_rule == PLURALITY_2_ROUNDS:
            return self.results[voting_rule][-1][0]
        if voting_rule == CONDORCET_SIMPLE:
            return self.choose_condorcet_winner()
        return self.results[voting_rule][0]

    def choose_condorcet_winner(self):
        fst_candidate = self.results[CONDORCET_SIMPLE][0]
        score = fst_candidate.scores[CONDORCET_SIMPLE]
        return fst_candidate if score == len(self.candidates) - 1 else None

    def init_results_keys(self, set_keys):
        for key in set_keys:
            self.results[key] = None

    def calculate_results(self):
        for voting_rule in self.results:
            self.apply_voting_rule(voting_rule)

    def delete_all_data(self):
        self.electors.clear()
        self.candidates.clear()
        self.results.clear()

    ### fonction sans argument appelée dans le main avant l'utilisation des fonctions de vote, créé les electors dans la base de donnée election
    def create_electors(self):
        for elec in self.electors_positions:
            self.add_elector(
                Elector(
                    candidates=self.candidates,
                    position=elec,
                )
            )
