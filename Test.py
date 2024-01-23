from math import sqrt

class Person:
    def __init__(self, position):
        self.position = position


class Candidate(Person):
    def __init__(self, position):
        super().__init__(position)
        scores_voting_systems = dict()

    pass


class Elector(Person):
    def __init__(self, position, candidate_ranking=[]):
        self.position = position
        if candidate_ranking == []:
            candidate_ranking = calculate_ranking_from_position()
        self.candidate_ranking = candidate_ranking

    # Calculate ranking from given position (x,y)
    def calculate_ranking_from_position(self, candidates):
        distances = get_list_distances_from_candidates()
        ranking = [
            c
            for (c,) in sorted(
                zip(candidates, distances), key=lambda t: t[1], reverse=True
            )
        ]
        return ranking

    def get_list_distances_from_candidates(self, list_candidates):
        distances = []
        x, y = self.position
        for candidate in list_candidates:
            x_c, y_c = candidate.getPostion()
            distances.append(sqrt((x_c - x) ^ 2 + (y_c - y) ^ 2))
        return distances