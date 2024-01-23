from math import sqrt
import random

class Person:
    def __init__(self, position):
        self.position = position

    def getPosition(self) :
        return (self.position)
    
    def __str__(self):
        return str(self.position)

    def __repr__(self):
        return self.__str__()


class Candidate(Person):
    def __init__(self, position):
        super().__init__(position)
        self.scores = dict()


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
            distances.append(sqrt((x_c - x)**2 + (y_c - y)**2))
        return distances
    
    # Calculate ranking from given position (x,y)
    def pos_to_rank(self, candidates):
        distances = self.dist_from_cand(candidates)
        print(distances)
        ranking = [
            c for (c,) in sorted(zip(candidates, distances), key=lambda t: t[1])
        ]
        return ranking


def create_cand(pos) :
    return Candidate(pos)


def liste_cand_rand(n) :
    liste_cand = []
    for _ in range(n):
        x=random.uniform(-1, 1)
        y=random.uniform(-1, 1)
        liste_cand.append(create_cand((x,y)))


def createListElector(listPos, listCandidate):
    listElector = []
    for i in listPos:
        listElector.append(Elector(i, listCandidate))
    return listElector


def createListElectorRand(n, listCandidate) :
    listElector = []
    for _ in range(n):
        x=random.uniform(-1, 1)
        y=random.uniform(-1, 1)
        listElector.append(Elector((x,y), listCandidate))
    return listElector
