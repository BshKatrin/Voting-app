from math import sqrt
from random import random

from .utls import Singleton, NameIterator, IdIterator

from .election_constants import RandomConstants, VotingRulesConstants
from .extensions import Polls, LiquidDemocracy

from .voting_rules.utls import Utls

from people import Candidate, Elector


class Election(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.electors = []
        self.candidates = []

        self.first_name_iter = NameIterator()
        self.last_name_iter = NameIterator()

        self.id_iter = IdIterator(0)

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
        self.poll_voting_rule = VotingRulesConstants.PLURALITY_SIMPLE
        self.tie_breaker_activated = True

        self.generation_constants = dict()
        for type, default_value in RandomConstants.DEFAULT_VALUES.items():
            self.generation_constants[type] = default_value

        # For polls
        self.directions_data = Polls.get_default_directions_data()

    def _init_results_keys(self, set_keys):
        for key in set_keys:
            self.results[key] = None

    def _calc_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def _has_electors_candidates(self):
        if not self.electors and not self.candidates:
            return False
        return True

    # For import only
    def add_elector_import(self, new_elector):
        if self.nb_polls:
            Polls.add_elector_data(self.directions_data, new_elector)
        self.electors.append(new_elector)

    def add_elector(self, position):
        knowledge_const = self.generation_constants[RandomConstants.KNOWLEDGE]
        new_elector = Elector(
            id=next(self.id_iter), position=position, knowledge_const=knowledge_const
        )
        x, y = new_elector.position

        if self.nb_polls:
            Polls.add_elector_data(self.directions_data, new_elector)

        # All electors average
        x_avg, y_avg = self.average_position_electors
        x_avg, y_avg = x_avg + x, y_avg + y
        self.average_position_electors = (x_avg, y_avg)
        self.electors.append(new_elector)

    # For import only
    def add_candidate_import(self, new_candidate):
        self.candidates.append(new_candidate)
        if self.nb_polls:
            Polls.add_candidate_data(self.directions_data, new_candidate)

    def add_candidate(self, position, first_name="", last_name=""):
        dogmat_const = self.generation_constants[RandomConstants.DOGMATISM]
        oppos_const = self.generation_constants[RandomConstants.OPPOSITION]

        first_name = next(self.first_name_iter) if not first_name else first_name
        last_name = next(self.last_name_iter) if not last_name else last_name

        new_candidate = Candidate(
            id=next(self.id_iter),
            position=position,
            first_name=first_name,
            last_name=last_name,
            dogmatism_const=dogmat_const,
            opposition_const=oppos_const,
        )
        if self.nb_polls:
            Polls.add_candidate_data(self.directions_data, new_candidate)

        self.candidates.append(new_candidate)

    def apply_voting_rule(self, voting_rule):
        if not self._has_electors_candidates():
            pass

        result = []
        func = VotingRulesConstants.VOTING_RULES_FUNC[voting_rule]

        if voting_rule in VotingRulesConstants.CONDORCET:
            result = func(self.electors, self.candidates, self.duels_scores)

        elif voting_rule == VotingRulesConstants.APPROVAL:
            result = func(
                self.electors,
                self.candidates,
                VotingRulesConstants.APPROVAL_GAP_COEF,
                self.duels_scores if self.tie_breaker_activated else None,
            )
        else:
            result = func(
                self.electors,
                self.candidates,
                self.duels_scores if self.tie_breaker_activated else None,
            )

        self.results[voting_rule] = result

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

    def _define_ranking(self):
        for elector in self.electors:
            elector.rank_candidates(self.candidates)

    def calc_results(self, imported=False):
        if imported:
            # Duels are imported in sqlite
            self.set_results()
            return

        self.duels_scores = Utls.set_duels_scores(self.electors, self.candidates)

        for voting_rule in self.results:
            self.apply_voting_rule(voting_rule)

    def set_avg_electors_position(self):
        x_avg, y_avg = self.average_position_electors
        x_avg /= len(self.electors)
        y_avg /= len(self.electors)
        self.average_position_electors = (x_avg, y_avg)

    # fonction sans argument appelée pour calculer le taux de satisfaction
    # de la population utilisé ensuite dans l'affichage des vainqueurs des éléctions
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
        return percentage

    # For import only
    def set_results(self):
        if not self._has_electors_candidates():
            return
        # Assuming every candidate has the same voting_rules
        candidate = self.candidates[0]
        keys = candidate.scores.keys()
        for voting_rule in keys:
            if voting_rule in VotingRulesConstants.ONE_ROUND:
                result = Utls.sort_cand_by_value(self.candidates, voting_rule)

            if voting_rule in VotingRulesConstants.MULTI_ROUND:
                self.results[voting_rule] = [None] * len(candidate.scores[voting_rule])
                # prettier-ignore
                for round in range(len(candidate.scores[voting_rule])):
                    result = Utls.sort_cand_by_round(
                        self.candidates, voting_rule, round
                    )

            if voting_rule in VotingRulesConstants.CONDORCET:
                sort_asc = (
                    True
                    if voting_rule == VotingRulesConstants.CONDORCET_SIMPSON
                    else False
                )

                result = Utls.sort_cand_by_value(self.candidates, voting_rule, sort_asc)

            self.results[voting_rule] = result

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

    def _make_delegations(self):
        for elector in self.electors:
            proba = 1 - elector.knowledge
            # No delegations
            if random() > proba:
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

    def conduct_poll(self):
        voting_rule = self.poll_voting_rule
        winner = self.choose_winner(voting_rule)
        ranking = self.results[voting_rule]

        Polls.change_position_candidates(
            self.candidates,
            winner,
            ranking,
            self.directions_data,
            self.generation_constants[RandomConstants.TRAVEL_DIST],
        )

        # Electors rank newly positioned candidates
        self._define_ranking()

        score_winner = winner.scores[voting_rule]
        Polls.change_ranking_electors(
            self.electors,
            score_winner,
            voting_rule,
            VotingRulesConstants.APPROVAL_GAP_COEF,
        )
        # Recalculate results
        self.calc_results()

    # def _clean_direction_data(self):
    #     self.directions_data.clear()

    def delete_all_data(self):
        self.electors.clear()
        self.candidates.clear()
        self.results.clear()

        self.first_name_iter.restart()
        self.last_name_iter.restart()
        self.id_iter.restart()

        self.directions_data.clear()
