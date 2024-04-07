from dataclasses import dataclass, field, InitVar
from typing import List, Tuple
from math import sqrt

from .person import Person
from .candidate import Candidate

from electoral_systems import RandomConstants


@dataclass(kw_only=True)
class Elector(Person):
    candidates_ranked: List[Candidate] = field(default_factory=list, repr=False)
    # weight = 0 -> delegation done
    # weight > 0 -> no delegation
    weight: int = 1
    knowledge: float = -1.0
    knowledge_const: InitVar[Tuple[float, float]] = RandomConstants.DEFAULT_VALUES[
        RandomConstants.KNOWLEDGE
    ]

    def __post_init__(self, knowledge_const):
        mu, sigma = knowledge_const
        if self.knowledge < 0:
            self.knowledge = Person.generate_parameter(
                mu=mu, sigma=sigma, lower_limit=0, upper_limit=1
            )

    def __str__(self):
        return (
            super().__str__()
            + f" weight : {self.weight}, knowledge : {self.knowledge:.2f}"
        )

    def __repr__(self):
        return self.__str__()

    def dist_from_cand(self, candidates):
        distances = []
        for candidate in candidates:
            distances.append(self.dist_from_one_cand(candidate))
        return distances

    def dist_from_one_cand(self, candidate):
        x, y = self.position
        x_c, y_c = candidate.get_position()
        return sqrt((x_c - x) ** 2 + (y_c - y) ** 2)

    # Calculate ranking from given position (x,y)
    def pos_to_rank(self, candidates):
        distances = self.dist_from_cand(candidates)
        ranking = [
            c for (c, _) in sorted(zip(candidates, distances), key=lambda t: t[1])
        ]
        return ranking

    def rank_candidates(self, candidates):
        self.candidates_ranked = self.pos_to_rank(candidates)
