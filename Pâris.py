from math import sqrt

class Person:
    def __init__(self, position):
        self.position = position

    def getPosition(self) :
        return self.position


class Candidate(Person):
    def __init__(self, position):
        super().__init__(position)
        self.scores = dict()


class Elector(Person):
    def __init__(self, position, candidate_ranking=[]):
        self.position = position
        if candidate_ranking == []:
            candidate_ranking = self.pos_to_rank()
        self.candidate_ranking = candidate_ranking

    def dist_from_cand(self, list_candidates):
        distances = []
        x, y = self.position
        for candidate in list_candidates:
            x_c, y_c = candidate.getPostion()
            distances.append(sqrt((x_c - x) ^ 2 + (y_c - y) ^ 2))
        return distances
    
    # Calculate ranking from given position (x,y)
    def pos_to_rank(self, candidates):
        distances = self.dist_from_cand(candidates)
        ranking = [
            c
            for (c,) in sorted(
                zip(candidates, distances), key=lambda t: t[1]
            )
        ]
        return ranking
        
