from math import sqrt

class Elector(Person):
    def __init__(self, position, candidates, candidate_ranking=[]):
        super().__init__(position)
        self.position = position
        if candidate_ranking == []:
            candidate_ranking = self.pos_to_rank(candidates)
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
