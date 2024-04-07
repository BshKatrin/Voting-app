from math import sqrt
from random import uniform, random

from numpy.random import normal
from numpy import std

from .election_constants import RandomConstants, VotingRulesConstants
from electoral_systems.extensions import Polls

from .voting_rules.tie import Tie
from .voting_rules.condorcet import set_duels_scores
from .extensions import LiquidDemocracy
from .voting_rules.utls import sort_cand_by_round, sort_cand_by_value
from .utls import Singleton


class Election(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.electors = []
        self.candidates = []

        self.results = dict()
        self.duels_scores = dict()

        # For satisfaction
        self.average_position_electors = (0, 0)
        self.proportion_satisfaction = 0

        # Init constants
        self.set_default_settings()

    def set_default_settings(self):
        self.nb_polls = 0
        self.liquid_democracy_activated = False
        self.liquid_democracy_voting_rule = VotingRulesConstants.PLURALITY_SIMPLE

        self.generation_constants = dict()
        for type, default_value in RandomConstants.DEFAULT_VALUES.items():
            self.generation_constants[type] = default_value

        # For polls
        self.directions_data = Polls.get_default_directions_data()

    def start_election(self, imported=False, chosen_voting_rules=None):
        self._define_ranking()
        self.set_avg_electors_position()
        self._calc_proportion_satisfaction()

        # Set data for polls
        if self.nb_polls:
            Polls.set_avg_electors_positions(self.directions_data)
            Polls.set_std_deviation(self.directions_data, len(self.electors))

        if self.liquid_democracy_activated:
            self._make_delegations()
        if chosen_voting_rules:
            self._init_results_keys(chosen_voting_rules)

        self.calc_results(imported)

    def _define_ranking(self):
        for elector in self.electors:
            elector.rank_candidates(self.candidates)

    def calc_results(self, imported=False):
        self.duels_scores = set_duels_scores(self.electors, self.candidates)
        if imported:
            self.set_results()
            return
        for voting_rule in self.results:

            self.apply_voting_rule(voting_rule)

    def set_avg_electors_position(self):
        x_avg, y_avg = self.average_position_electors
        x_avg /= len(self.electors)
        y_avg /= len(self.electors)
        self.average_position_electors = (x_avg, y_avg)

    def add_elector(self, new_elector):
        x, y = new_elector.position

        if self.nb_polls:
            Polls.add_elector_data(self.directions_data, new_elector)

        # All electors average
        x_avg, y_avg = self.average_position_electors
        x_avg, y_avg = x_avg + x, y_avg + y
        self.average_position_electors = (x_avg, y_avg)

        self.electors.append(new_elector)

    def add_candidate(self, new_candidate):
        if self.nb_polls:
            Polls.add_candidate_data(self.directions_data, new_candidate)

        self.candidates.append(new_candidate)

    def _has_electors_candidates(self):
        if not self.electors and not self.candidates:
            return False
        return True

    def _make_delegations(self):
        for elector in self.electors:
            proba = 1 - elector.knowledge
            # No delegations
            if uniform(0, 1) > proba:
                continue
            # Make delegation
            possible_delegees = LiquidDemocracy.choose_possible_delegees(
                self.electors, elector
            )
            delegee = LiquidDemocracy.choose_delegee(possible_delegees)
            if delegee is None:
                continue
            delegee.weight += elector.weight
            elector.weight = 0

    def apply_voting_rule(self, voting_rule):
        if not self._has_electors_candidates():
            pass

        if voting_rule == VotingRulesConstants.APPROVAL:
            self.results[voting_rule] = VotingRulesConstants.VOTING_RULES_FUNC[
                voting_rule
            ](self.electors, self.candidates, VotingRulesConstants.APPROVAL_GAP_COEF)
        else:
            self.results[voting_rule] = VotingRulesConstants.VOTING_RULES_FUNC[
                voting_rule
            ](self.electors, self.candidates)

        ties = Tie.get_ties(self.results[voting_rule], voting_rule)
        if ties:
            Tie.resolve_ties(self.results[voting_rule], ties, self.duels_scores)

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

    def _init_results_keys(self, set_keys):
        for key in set_keys:
            self.results[key] = None

    # For import only
    def set_results(self):
        if not self._has_electors_candidates():
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

    def _calc_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    ### fonction sans argument appelée pour calculer le taux de satisfaction de la population utilisé ensuite dans l'affichage des vainqueurs des éléctions
    def _calc_proportion_satisfaction(self):
        proportion = 0
        for candidate in self.candidates:
            dist_cand_electors = self._calc_distance(
                candidate.position, self.average_position_electors
            )
            proportion = max(proportion, dist_cand_electors)
        self.proportion_satisfaction = proportion

    def calc_satisfaction(self, candidate):
        diff = abs(
            self._calc_distance(candidate.position, self.average_position_electors)
            - self.proportion_satisfaction
        )
        percentage = (
            diff / self.proportion_satisfaction * 100
            if self.proportion_satisfaction != 0
            else 0
        )
        # print(candidate, percentage)
        return percentage

    def update_data_poll(self):
        # Recalc satisfaction 'cause of movement of candidates
        # Redefine ranking after candidates change their positions
        # self._define_ranking()
        self.calc_results()
        for vr, res in self.results.items():
            for c in res:
                print(c, c.scores[vr])

    def conduct_poll(self):
        voting_rule = self.liquid_democracy_voting_rule
        winner = self.choose_winner(voting_rule)
        ranking = self.results[voting_rule]

        Polls.change_position_candidates(
            self.candidates,
            winner,
            ranking,
            self.directions_data,
            self.generation_constants[RandomConstants.TRAVEL_DIST],
        )

        self._define_ranking()

        score_winner = winner.scores[voting_rule]
        Polls.change_ranking_electors(
            self.electors,
            score_winner,
            voting_rule,
            VotingRulesConstants.APPROVAL_GAP_COEF,
        )
        self.update_data_poll()

    def _clean_direction_data(self):
        self.directions_data.clear()

    def delete_all_data(self):
        self.electors.clear()
        self.candidates.clear()
        self.results.clear()
        self.directions_data.clear()
