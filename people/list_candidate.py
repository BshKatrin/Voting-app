from .candidate import Candidate
import random

def create_cand(pos) :
    return Candidate(pos)


def liste_cand_rand(n) :
    liste_cand = []
    for _ in range(n):
        x=random.uniform(-1, 1)
        y=random.uniform(-1, 1)
        liste_cand.append(create_cand((x,y)))

