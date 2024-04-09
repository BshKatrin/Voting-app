from numpy import std
from math import sqrt
from random import random


class Polls:
    AVG = "AVG"
    STD_DEV = "STD"
    ELECTORS = "ELECS"
    NB_CANDIDATES = "NBC"
    NB_ELECTORS = "NBE"

    NE = "NE"
    NW = "NW"
    SE = "SE"
    SW = "SW"
    CENTER = "CNT"

    def calc_distance(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def add_elector_data(directions_data, new_elector):
        x, y = new_elector.position

        directions = {
            Polls.in_center(new_elector.position),
            Polls.choose_direction(new_elector.position),
        }
        for direction in directions:
            if direction:
                x_avg, y_avg = directions_data[direction][Polls.AVG]
                x_avg, y_avg = x_avg + x, y_avg + y

                directions_data[direction][Polls.AVG] = (x_avg, y_avg)
                directions_data[direction][Polls.ELECTORS].append(new_elector)
                directions_data[direction][Polls.NB_ELECTORS] += 1

    def add_candidate_data(directions_data, new_candidate):
        directions = {
            Polls.in_center(new_candidate.position),
            Polls.choose_direction(new_candidate.position),
        }
        for direction in directions:
            if direction:
                directions_data[direction][Polls.NB_CANDIDATES] += 1

    def get_default_directions_data():
        directions = {Polls.NE, Polls.NW, Polls.SE, Polls.SW, Polls.CENTER}
        directions_data = dict()
        for direction in directions:
            directions_data[direction] = Polls._get_default_direction_data(
                direction)
        return directions_data

    def _get_default_direction_data(direction):
        return {
            Polls.AVG: (0, 0),
            Polls.STD_DEV: 0,
            Polls.NB_ELECTORS: 0,
            Polls.ELECTORS: [],  # For std deviation
            Polls.NB_CANDIDATES: 0,
        }

    def in_center(position):
        x, y = position
        if abs(x) < 0.3 and abs(y) < 0.3:
            return Polls.CENTER
        return None

    def choose_direction(position):
        x, y = position
        if x > 0 and y > 0:
            return Polls.NE
        if x > 0 and y < 0:
            return Polls.SE
        if x < 0 and y > 0:
            return Polls.NW
        if x < 0 and y < 0:
            return Polls.SW

    # For directions only
    def set_avg_electors_positions(directions_data):
        for direction, data in directions_data.items():
            (x_avg,
             y_avg), nb_electors = data[Polls.AVG], data[Polls.NB_ELECTORS]
            x_avg = x_avg / nb_electors if nb_electors else 0
            y_avg = y_avg / nb_electors if nb_electors else 0
            directions_data[direction][Polls.AVG] = (x_avg, y_avg)

    def set_std_deviation(directions_data, total_nb_electors):
        for direction in directions_data:
            direct_electors = directions_data[direction][Polls.ELECTORS]

            # Zero values wont be counted
            if len(direct_electors) == 0:
                continue

            direct_x = [elector.position[0] for elector in direct_electors]
            direct_y = [elector.position[1] for elector in direct_electors]

            # Take average value
            directions_data[direction][Polls.STD_DEV] = (
                std(direct_x) + std(direct_y)
            ) / 2
            # To make it equal to other parameters
            directions_data[direction][Polls.NB_ELECTORS] /= total_nb_electors
            directions_data[direction][Polls.ELECTORS].clear()

    # Posssible allies is a sublist of candidate whose score is higher than that of a candidate
    # Function return True iff alliance is formed, we dont care with whom
    def alliance_formed(candidate, possible_allies):
        # Conditions :
        # 1. Score of an ally > candidate
        # 2. Ally is in a circle of a candidate
        for ally in possible_allies:
            dist = Polls.calc_distance(candidate.position, ally.position)
            if dist < 0.15:
                return True
        return False

    def get_avg_directions_positions(directions_data, chosen_directions):
        avg_positions = []
        for direction, _ in chosen_directions:
            avg_positions.append(directions_data[direction][Polls.AVG])
        return avg_positions

    def choose_directions_by_scores(directions_scores):
        lst = [(direct, score) for direct, score in directions_scores.items()]
        lst = sorted(lst, key=lambda e: e[1])

        # Gap between 1st min and next values
        percentage = 1.6
        min = lst[0][1]
        chosen = []
        for direct, score in lst:
            if score < min * percentage:
                chosen.append((direct, score))
                percentage -= 0.3
        return chosen

    def get_directions_scores(directions_data, candidate):
        directions_scores = {direct: 0 for direct in directions_data}
        for direction, data in directions_data.items():
            # To avoid to choose that direction
            if directions_data[direction][Polls.NB_ELECTORS] <= 0.2:
                directions_scores[direction] = float("inf")
                continue
            dist = Polls.calc_distance(candidate.position, data[Polls.AVG])
            # Weighted sum.
            # Goal : Min dist, std_dev, nb_candidates. Max nb_electors (min negative value)
            score = (
                0.5 * dist
                + 0.2 * directions_data[direction][Polls.STD_DEV]
                - 0.2 * directions_data[direction][Polls.NB_ELECTORS]
                + 0.1 * directions_data[direction][Polls.NB_CANDIDATES]
            )

            directions_scores[direction] = score
        return directions_scores

    def move_in_direction(directions_data, candidate, travel_dist):
        # Init direction scores (weighted sum)
        directions_scores = Polls.get_directions_scores(
            directions_data, candidate)
        # Choose direction(s) with minimals scores
        chosen_directions = Polls.choose_directions_by_scores(
            directions_scores)
        # Move candidate to one (or several) avg positions of chosen directions
        avg_positions = Polls.get_avg_directions_positions(
            directions_data, chosen_directions
        )
        candidate.move_to_avg(avg_positions, travel_dist)

    # Returns True iff candidate gives up
    def give_up(candidate):
        return random() < 1 - candidate.dogmatism

    def change_position_candidates(
        candidates, winner, ranking, directions_data, travel_dist
    ):
        for i, candidate in enumerate(ranking):
            # If candidate is already the winner, he does NOT move
            if candidate == winner:
                continue
            # Check if candidate moves at all
            # If dogmacy is high -> low change to move
            # Dogmacy is low -> high change to move

            # Candidate is very dogmatic he prefers not to change his position
            if random() < candidate.dogmatism:
                continue

            # Gives up only if
            if Polls.give_up(candidate) and Polls.alliance_formed(candidate, ranking[:i]):
                # Alliance? Only if not opposed
                candidates.remove(candidate)
                continue
            # If no alliance, move in a winner direction
            # Based on opposition. Opposition is high -> low chance. Opposition is low -> high chance
            if random() < 1 - candidate.opposition:
                candidate.move_to_point(winner.position, travel_dist)
                continue
            # Else, move based on weighted sum
            Polls.move_in_direction(directions_data, candidate, travel_dist)

    def change_ranking_electors(electors, score_winner, voting_rule, approval_gap):
        for elector in electors:
            if random() < elector.knowledge:
                continue

            # Elector changes his vote
            # Rearrange his rank
            for i, candidate in enumerate(elector.candidates_ranked):
                circle_limit = (1 - elector.knowledge) * approval_gap

                if elector.dist_from_one_cand(candidate) > circle_limit:
                    break

                score_ratio = candidate.scores[voting_rule] / score_winner
                if random() < score_ratio:
                    # New candidate to vote for
                    chosen_candidate = candidate
                    # Shift candidates on a right
                    for j in range(i, 0, -1):
                        elector.candidates_ranked[j] = elector.candidates_ranked[j - 1]
                    elector.candidates_ranked[0] = chosen_candidate
                    break

            # Elector changes his vote
