from dataclasses import dataclass, field, InitVar
from typing import List
from math import sqrt

from .person import Person
from .candidate import Candidate


@dataclass(kw_only=True)
class Elector(Person):
    candidates: InitVar[List[Candidate]]
    candidates_ranked: List[Candidate] = field(default_factory=list, repr=False)

    def __post_init__(self, candidates):
        if not self.candidates_ranked:
            self.candidates_ranked = self.pos_to_rank(candidates)

    def dist_from_cand(self, candidates):
        distances = []
        x, y = self.position
        for candidate in candidates:
            x_c, y_c = candidate.get_position()
            distances.append(sqrt((x_c - x) ** 2 + (y_c - y) ** 2))
        return distances

    def dist_from_one_cand(self,candidate):
        x,y=self.position
        xc,yc=candidate.get_position()
        return (sqrt((xc-x)**2+ (yc-y)**2)) 
    

    # Calculate ranking from given position (x,y)
    def pos_to_rank(self, candidates):
        distances = self.dist_from_cand(candidates)
        ranking = [
            c for (c, _) in sorted(zip(candidates, distances), key=lambda t: t[1])
        ]
        return ranking

    # Retourne une liste des electeurs genere de maniere aleatoire
    @classmethod
    def gen_rand_electors(cls, n, candidates):
        return [Elector(candidates=candidates) for _ in range(n)]
