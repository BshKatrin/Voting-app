from copy import deepcopy
from dataclasses import dataclass, field
from random import choices
from string import ascii_uppercase
from typing import Dict, Union, List
from itertools import product

from .person import Person


def generator_names():
    for length in range(1, 5):
        for combination in product(ascii_uppercase, repeat=length):
            yield "".join(combination)


generator_first_name = generator_names()
generator_last_name = generator_names()


@dataclass(kw_only=True, unsafe_hash=True, eq=True, order=True)
# Keep in mind that no guarantee for unique first_name and last_name
class Candidate(Person):

    first_name: str = ""
    last_name: str = ""

    # int -> 1 round, float -> Copeland, List -> N rounds
    scores: Dict[str, Union[int, float, List[int]]] = field(
        default_factory=dict, hash=False, compare=False
    )

    def __post_init__(self):
        if not self.first_name:
            self.first_name = next(generator_first_name)
        if not self.last_name:
            self.last_name = next(generator_last_name)

    def __str__(self):
        x, y = self.position
        # return f"Candidate({self.id}, ({x:.2f},{y:.2f}), {self.first_name}, {self.last_name}, {self.scores})"
        return f"Candidate({self.id}, {self.first_name} {self.last_name})"

    def __repr__(self):
        return self.__str__()

    def init_score(self, voting_system_name, new_score, list_type=False):
        if not list_type:
            self.scores[voting_system_name] = new_score
        else:
            self.scores[voting_system_name] = deepcopy(new_score)

    def add_score(self, voting_system_name, score):
        if voting_system_name not in self.scores:
            self.init_score(voting_system_name, 0)
        self.scores[voting_system_name] += score

    # Round commence a partir de 0
    def add_score_round(self, voting_system_name, score, round):
        # OU try ... except (if key not in scores) -> a voir
        if voting_system_name not in self.scores:
            self.init_score(voting_system_name, [0] * round, True)
        self.scores[voting_system_name][round] += score
