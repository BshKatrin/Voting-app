from math import sqrt
import random


class Person:
    def __init__(self, position):
        self.position = position

    def getPostion(self):
        return self.position

    def __str__(self):
        return str(self.position)

    def __repr__(self):
        return self.__str__()


class Candidate(Person):
    def __init__(self, position):
        super().__init__(position)
        scores_voting_systems = dict()


class Elector(Person):
    def __init__(self, position, candidates, candidate_ranking=[]):
        super().__init__(position)
        if candidate_ranking == []:
            candidate_ranking = self.pos_to_rank(candidates)
        self.candidate_ranking = candidate_ranking

    # Calculate ranking from given position (x,y)
    def pos_to_rank(self, candidates):
        distances = self.dist_from_cand(candidates)
        print(distances)
        ranking = [
            c for (c, _) in sorted(zip(candidates, distances), key=lambda t: t[1])
        ]
        return ranking

    def dist_from_cand(self, list_candidates):
        distances = []
        x, y = self.position
        for candidate in list_candidates:
            x_c, y_c = candidate.getPostion()

            distances.append(sqrt((x_c - x) ** 2 + (y_c - y) ** 2))
        return distances

