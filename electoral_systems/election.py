from copy import deepcopy
from math import sqrt
from random import uniform, random

from numpy.random import normal

from .election_constants import RandomConstants, VotingRulesConstants

from .voting_rules.condorcet import set_duels_scores
from .voting_rules.delegation import choose_delegee, choose_possible_delegees
from .voting_rules.utls import sort_cand_by_round, sort_cand_by_value
from .singleton import Singleton


class Election(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.electors = []
        self.candidates = []

        self.results = dict()
        self.condorcet_graph_info = dict()

        self.average_position_electors = (0, 0)
        self.proportion_satisfaction = 0

        self.set_default_settings()

    def start_election(self, imported=False, chosen_voting_rules=None):
        # Make every elector rank candidates
        self.define_ranking()
        self.set_average_electors_position()
        self.calculate_prop_satisfation()

        if self.liquid_democracy_activated:
            self.make_delegations()
        if chosen_voting_rules:
            self.init_results_keys(chosen_voting_rules)

        self.calculate_results(imported)

    def set_default_settings(self):
        self.nb_polls = 5
        self.liquid_democracy_activated = True

        # variable necessaire pour generation aleatoire
        self.generation_constants = {
            RandomConstants.ECONOMICAL: (0, 0.5),
            RandomConstants.SOCIAL: (0, 0.5),
            RandomConstants.ORIENTATION: 1,
            RandomConstants.KNOWLEDGE: (0.5, 0.3),
            RandomConstants.DOGMATISM: (0, 0.5),
            RandomConstants.OPPOSITION: (0, 0.5),
            RandomConstants.TRAVEL_DIST: 0.1,
        }

        # self.economical_constants = (280, 100)
        # self.social_constants = (280, 100)
        # self.coef_dir = 1

        # self.knowledge_constants = (0.5, 0.3)

    def define_ranking(self):
        for elector in self.electors:
            elector.rank_candidates(self.candidates)

    def set_average_electors_position(self):
        x, y = self.average_position_electors
        x /= len(self.electors)
        y /= len(self.electors)
        self.average_position_electors = (x, y)

    def add_elector(self, new_elector):
        x, y = new_elector.position
        x_avg, y_avg = self.average_position_electors
        x_avg += x
        y_avg += y
        self.average_position_electors = (x_avg, y_avg)
        self.electors.append(new_elector)

    def add_candidate(self, new_candidate):
        self.candidates.append(new_candidate)

    def add_candidates(self, candidates):
        self.candidates = deepcopy(candidates)

    def add_electors(self, electors):
        self.electors = deepcopy(electors)

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

        if voting_rule in VotingRulesConstants.CONDORCET:
            self.condorcet_graph_info = set_duels_scores(self.electors, self.candidates)

        self.results[voting_rule] = VotingRulesConstants.VOTING_RULES_FUNC[voting_rule](
            self.electors, self.candidates
        )

    def choose_winner(self, voting_rule):
        if voting_rule not in self.results:
            self.apply_voting_rule(voting_rule)

        if voting_rule in VotingRulesConstants.MULTI_ROUND:
            return self.results[voting_rule][-1][0]

        if voting_rule == VotingRulesConstants.CONDORCET_SIMPLE:
            return self.choose_condorcet_winner()

        return self.results[voting_rule][0]

    def choose_condorcet_winner(self):
        fst_candidate = self.results[VotingRulesConstants.CONDORCET_SIMPLE][0]
        score = fst_candidate.scores[VotingRulesConstants.CONDORCET_SIMPLE]
        return fst_candidate if score == len(self.candidates) - 1 else None

    def init_results_keys(self, set_keys):
        for key in set_keys:
            self.results[key] = None

    def set_results(self):
        if not self.has_electors_candidates:
            return

        # Assuming every candidate has the same voting_rules
        candidate = self.candidates[0]
        keys = candidate.scores.keys()

        for voting_rule in keys:
            if voting_rule in VotingRulesConstants.ONE_ROUND:
                result = sort_cand_by_value(self.candidates, voting_rule)
                self.results[voting_rule] = result
            elif voting_rule in VotingRulesConstants.MULTI_ROUND:
                self.results[voting_rule] = [None] * len(candidate.scores[voting_rule])
                for round in range(len(candidate.scores[voting_rule])):
                    result = sort_cand_by_round(self.candidates, voting_rule, round)
                    self.results[voting_rule][round] = result
            elif voting_rule in VotingRulesConstants.CONDORCET:
                sort_asc = (
                    True
                    if voting_rule == VotingRulesConstants.CONDORCET_SIMPSON
                    else False
                )

                result = sort_cand_by_value(self.candidates, voting_rule, sort_asc)
                self.results[voting_rule] = result

        for voting_rule, res in self.results.items():
            print(voting_rule, res)

    def calculate_results(self, imported=False):
        if imported:
            self.set_results()
            return
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

    ### fonction sans argument appelée pour calculer le taux de satisfaction de la population utilisé ensuite dans l'affichage des vainqueurs des éléctions
    def calculate_prop_satisfation(self):
        proportion = 0
        for candidate in self.candidates:
            dist_cand_electors = self._calculate_distance(
                candidate.position, self.average_position_electors
            )
            proportion = max(proportion, dist_cand_electors)
        # print("Proportion", proportion)
        self.proportion_satisfaction = proportion

    def calculate_satisfaction(self, candidate):
        diff = abs(
            self._calculate_distance(candidate.position, self.average_position_electors)
            - self.proportion_satisfaction
        )
        percentage = (
            diff / self.proportion_satisfaction * 100
            if self.proportion_satisfaction != 0
            else 0
        )
        # print(candidate, percentage)
        return percentage

    # Apply poll for every 1 ROUND voting system
    def _conduct_poll_voting_rule(self, voting_rule):
        pass

    # Conduct polls for every chosen 1 round voting rule
    def conduct_polls(self, voting_rules):
        # Choose 1 ROUND voting rules
        voting_rules_one_round = VotingRulesConstants.ONE_ROUND & self.results.keys()

        for voting_rule in voting_rules_one_round:
            self._conduct_poll_voting_rule(voting_rule)
