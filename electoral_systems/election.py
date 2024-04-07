from math import sqrt
from random import uniform, random

from numpy.random import normal
from numpy import std

from .election_constants import RandomConstants, VotingRulesConstants

from .voting_rules.condorcet import set_duels_scores
from .extensions.liquid_democracy import choose_delegee, choose_possible_delegees
from .voting_rules.utls import sort_cand_by_round, sort_cand_by_value
from .utls import Singleton


class Election(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.electors = []
        self.candidates = []

        self.results = dict()
        self.duels_scores = dict()

        self.average_position_electors = (0, 0)  # For satisfaction

        self.proportion_satisfaction = 0

        self.set_default_settings()

    def set_default_settings(self):
        self.nb_polls = 5
        self.liquid_democracy_activated = True
        self.liquid_democracy_voting_rule = VotingRulesConstants.PLURALITY_SIMPLE

        self.generation_constants = dict()
        for type, default_value in RandomConstants.DEFAULT_VALUES.items():
            self.generation_constants[type] = default_value

        # For polls
        self.directions_data = {
            "CENTER": self._init_direction_data(),
            "NW": self._init_direction_data(),
            "NE": self._init_direction_data(),
            "SW": self._init_direction_data(),
            "SE": self._init_direction_data(),
        }

    def start_election(self, imported=False, chosen_voting_rules=None):
        self._define_ranking()
        self._set_avg_electors_position()
        self._set_std_deviation()
        self._calc_proportion_satisfaction()

        if self.liquid_democracy_activated:
            self._make_delegations()
        if chosen_voting_rules:
            self._init_results_keys(chosen_voting_rules)

        self.calc_results(imported)

    def _define_ranking(self):
        for elector in self.electors:
            elector.rank_candidates(self.candidates)

    def calc_results(self, imported=False):
        if imported:
            self.set_results()
            return
        for voting_rule in self.results:
            self.apply_voting_rule(voting_rule)

    def _init_direction_data(self):
        return {
            "AVG": (0, 0),
            "STD_DEV": 0,
            "NB_ELECTORS": 0,
            "ELECTORS": [],  # For std deviation
            "NB_CANDIDATES": 0,
        }

    # Call after average is set
    def _set_std_deviation(self):
        for direct in self.directions_data:
            direct_electors = self.directions_data[direct]["ELECTORS"]

            # Zero values wont be counted
            if len(direct_electors) == 0:
                continue

            direct_x = [elector.position[0] for elector in direct_electors]
            direct_y = [elector.position[1] for elector in direct_electors]

            # Take average value
            self.directions_data[direct]["STD_DEV"] = (
                std(direct_x) + std(direct_y)
            ) / 2
            # To make it equal to other parameters
            self.directions_data[direct]["NB_ELECTORS"] /= len(self.electors)
            self.directions_data[direct]["ELECTORS"].clear()

    def _choose_direction(self, position):
        x, y = position
        if x > 0 and y > 0:
            return "NE"
        if x > 0 and y < 0:
            return "SE"
        if x < 0 and y > 0:
            return "NW"
        if x < 0 and y < 0:
            return "SW"

    # Center is considered between -0.3 and 0.3
    def _in_center(self, position):
        x, y = position
        if abs(x) < 0.3 and abs(y) < 0.3:
            return "CENTER"
        return None

    def _set_avg_electors_position(self):
        for direct, data in self.directions_data.items():
            (x_avg, y_avg), nb_electors = data["AVG"], data["NB_ELECTORS"]
            x_avg = x_avg / nb_electors if nb_electors else 0
            y_avg = y_avg / nb_electors if nb_electors else 0
            self.directions_data[direct]["AVG"] = (x_avg, y_avg)

        # All electors average
        x_avg, y_avg = self.average_position_electors
        x_avg /= len(self.electors)
        y_avg /= len(self.electors)

    def add_elector(self, new_elector):
        x, y = new_elector.position

        # Center
        if self._in_center(new_elector.position):
            x_avg, y_avg = self.directions_data["CENTER"]["AVG"]
            x_avg, y_avg = x_avg + x, y_avg + y
            self.directions_data["CENTER"]["AVG"] = (x_avg, y_avg)
            self.directions_data["CENTER"]["ELECTORS"].append(new_elector)
            self.directions_data["CENTER"]["NB_ELECTORS"] += 1

        direct = self._choose_direction(new_elector.position)
        x_avg, y_avg = self.directions_data[direct]["AVG"]
        x_avg, y_avg = x_avg + x, y_avg + y
        self.directions_data[direct]["AVG"] = (x_avg, y_avg)
        self.directions_data[direct]["ELECTORS"].append(new_elector)
        self.directions_data[direct]["NB_ELECTORS"] += 1

        # All electors average
        x_avg, y_avg = self.average_position_electors
        self.average_position_electors = (x_avg, y_avg)

        self.electors.append(new_elector)

    def add_candidate(self, new_candidate):
        x, y = new_candidate.position
        if self._in_center(new_candidate.position):
            x_avg, y_avg = self.directions_data["CENTER"]["AVG"]
            x_avg, y_avg = x_avg + x, y_avg + y
            self.directions_data["CENTER"]["AVG"] = (x_avg, y_avg)
            self.directions_data["CENTER"]["NB_CANDIDATES"] += 1

        direct = self._choose_direction(new_candidate.position)
        self.directions_data[direct]["NB_CANDIDATES"] += 1
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
            delegee = choose_delegee(choose_possible_delegees(self.electors, elector))
            if delegee is None:
                continue
            delegee.weight += elector.weight
            elector.weight = 0

    def apply_voting_rule(self, voting_rule):
        if not self._has_electors_candidates():
            pass

        if voting_rule in VotingRulesConstants.CONDORCET:
            self.duels_scores = set_duels_scores(self.electors, self.candidates)

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

    # Apply poll for 1 ROUND voting rule
    def _change_ranking_electors(self):
        # Protection
        voting_rule = self.liquid_democracy_voting_rule
        if voting_rule not in self.results:
            self.apply_voting_rule(voting_rule)

        score_max = self.choose_winner(voting_rule).scores[voting_rule]
        for elector in self.electors:
            if random() < elector.knowledge:
                continue

            # Elector changes his vote
            # Rearrange his rank
            for i, candidate in enumerate(elector.candidates_ranked):
                circle_limit = (
                    1 - elector.knowledge
                ) * VotingRulesConstants.APPROVAL_GAP_COEF

                if elector.dist_from_one_cand(candidate) > circle_limit:
                    break

                score_ratio = candidate.scores[voting_rule] / score_max
                if random() < score_ratio:
                    # New candidate to vote for
                    chosen_candidate = candidate
                    # Shift candidates on a right
                    for j in range(i, 0, -1):
                        elector.candidates_ranked[j] = elector.candidates_ranked[j - 1]
                    elector.candidates_ranked[0] = chosen_candidate
                    break
            # Elector changes his vote

    def _choose_directions_scores(self, directions_scores):
        lst = [(direct, score) for direct, score in directions_scores.items()]
        lst = sorted(lst, key=lambda e: e[1])

        # Gap between 1st min and next values
        percentage = 1.6
        mn = lst[0][1]
        chosen = []
        for direct, score in lst:
            if score < mn * percentage:
                chosen.append((direct, score))
                percentage -= 0.3
        return chosen

    def _move_candidate(self, candidate, chosen_directions):
        avg_positions = []
        for direct, _ in chosen_directions:
            avg_positions.append(self.directions_data[direct]["AVG"])
        candidate.move_to_avg(
            avg_positions, self.generation_constants[RandomConstants.TRAVEL_DIST]
        )

    def _move_in_direction(self, candidate):
        directions_scores = {direct: 0 for direct in self.directions_data}
        for direct, data in self.directions_data.items():
            # To avoid to choose that direction
            if self.directions_data[direct]["NB_ELECTORS"] <= 0.2:
                directions_scores[direct] = float("inf")
                continue
            dist = self._calc_distance(candidate.position, data["AVG"])
            # Weighted sum.
            # Goal : Min dist, std_dev, nb_candidates. Max nb_electors (min negative value)
            score = (
                0.5 * dist
                + 0.2 * self.directions_data[direct]["STD_DEV"]
                - 0.2 * self.directions_data[direct]["NB_ELECTORS"]
                + 0.1 * self.directions_data[direct]["NB_CANDIDATES"]
            )

            directions_scores[direct] = score
        chosen_directions = self._choose_directions_scores(directions_scores)
        self._move_candidate(candidate, chosen_directions)

    # Posssible allies is a sublist of candidate whose score is higher than that of a candidate
    # Function return True iff alliance is formed, we dont care with whom
    def _alliance_formed(self, candidate, possible_allies):
        # Conditions :
        # 1. Score of an ally > candidate
        # 2. Ally is in a circle of a candidate
        for ally in possible_allies:
            dist = self._calc_distance(candidate.position, ally.position)
            if dist == 0.0:
                return True
            if random() < 1 / ((dist * 10) ** 2):
                return True
        return False

    def _change_position_candidates(self):
        curr_winner = self.choose_winner(self.liquid_democracy_voting_rule)
        curr_ranking = self.results[self.liquid_democracy_voting_rule]
        for i, candidate in enumerate(curr_ranking):
            # If candidate is already the winner, he does NOT move
            if candidate == curr_winner:
                continue
            # Check if candidate moves at all
            # If dogmacy is high -> low change to move
            # Dogmacy is low -> high change to move
            if random() > 1 - candidate.dogmatism:
                continue
            # Candidate moves.
            # Alliance?
            if self._alliance_formed(candidate, curr_ranking[:i]):
                self.candidates.remove(candidate)
                continue
            # If no alliance, move in a winner direction
            # Based on opposition. Opposition is high -> low chance. Opposition is low -> high chance
            if random() < 1 - candidate.opposition:
                candidate.move_to_point(
                    curr_winner.position,
                    self.generation_constants[RandomConstants.TRAVEL_DIST],
                )
                continue
            # Else, move based on weighted sum
            self._move_in_direction(candidate)

    def update_data_poll(self):
        # Recalc satisfaction 'cause of movement of candidates
        # Redefine ranking after candidates change their positions
        # self._define_ranking()
        self.calc_results()
        for vr, res in self.results.items():
            for c in res:
                print(c, c.scores[vr])

    def conduct_poll(self):
        self._change_position_candidates()
        self._define_ranking()
        self._change_ranking_electors()
        self.update_data_poll()

    def _clean_direction_data(self):
        self.directions_data.clear()

    def delete_all_data(self):
        self.electors.clear()
        self.candidates.clear()
        self.results.clear()
        self.directions_data.clear()
