from copy import deepcopy
from math import sqrt
from random import uniform
from people import Candidate
from people import Elector
import numpy as np

from electoral_systems.voting_rules.constants import *
from .func_constants import VOTING_RULES_FUNC

from .voting_rules.constants import *
from .voting_rules.condorcet import set_duels_scores
from .voting_rules.delegation import choose_delegee, choose_possible_delegees
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

        self.average_position_electors = (0, 0)
        self.proportion_satisfaction = 0

        # variable necessaire pour generation aleatoire
        self.economical_constants = (280, 100)
        self.social_constants = (280, 100)
        self.coef_dir = 1

        self.knowledge_constants = (0.5, 0.3)

        self.nb_polls = 5

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

    def make_delegations(self):
        for elector in self.electors:
            proba = 1 - elector.knowledge
            # print(f"proba{proba:.2f}")
            # print("no delegation")
            # No delegation
            if uniform(0, 1) > proba:
                continue
            # Make delegation
            delegee = choose_delegee(choose_possible_delegees(self.electors, elector))
            if delegee is None:
                continue
            # print("delegation to ", delegee)
            delegee.weight += elector.weight
            elector.weight = 0

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
        if voting_rule in {EXHAUSTIVE_BALLOT, PLURALITY_2_ROUNDS}:
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

    def _calculate_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    ### fonction sans argument appelée dans le main avant l'utilisation des fonctions de vote, créé les electors dans la base de donnée election
    def create_electors(self):
        nb_electors = 0
        x_average = 0
        y_average = 0
        for elec in self.electors_positions:
            nb_electors += 1

            (x_elec, y_elec) = elec
            x_average += x_elec
            y_average += y_elec
            (mu, sigma) = self.knowledge_constants

            random_knowledge = np.random.normal(mu, sigma, None)
            while random_knowledge > 1:
                random_knowledge = np.random.normal(mu, sigma, None)

            self.add_elector(
                Elector(
                    candidates=self.candidates,
                    position=elec,
                    knowledge=random_knowledge,
                )
            )
        x_average = x_average / nb_electors
        y_average = y_average / nb_electors
        self.average_position_electors = (x_average, y_average)
        self.electors_positions.clear()

    ### fonction sans argument appelée pour calculer le taux de satisfaction de la population utilisé ensuite dans l'affichage des vainqueurs des éléctions
    def calculate_prop_satisfation(self):
        proportion = 0
        for candidate in self.candidates:
            dist_cand_electors = self._calculate_distance(
                candidate.position, self.average_position_electors
            )
            proportion = max(proportion, dist_cand_electors)

        self.proportion_satisfaction = proportion

    def calculate_satisfaction(self, candidate):
        diff = abs(
            self._calculate_distance(candidate.position, self.average_position_electors)
            - self.proportion_satisfaction
        )
        percentage = diff / self.proportion_satisfaction * 100
        return percentage
