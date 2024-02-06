from copy import deepcopy
from dataclasses import dataclass, field
from random import choices
from string import ascii_lowercase
from typing import Dict, Union, List

from .person import Person


@dataclass(kw_only=True, unsafe_hash=True, eq=True)
# Keep in mind that no guarantee for unique first_name and last_name
class Candidate(Person):
    def gen_first_name():
        return "".join(choices(ascii_lowercase, k=10))

    def gen_last_name():
        return "".join(choices(ascii_lowercase, k=10))

    first_name: str = field(default_factory=gen_first_name)
    last_name: str = field(default_factory=gen_last_name)

    # int -> 1 round, float -> Copeland, List -> N rounds
    scores: Dict[str, Union[int, float, List[int]]] = field(
        default_factory=dict, hash=False, compare=False
    )

    def __str__(self):
        x, y = self.position
        # return f"Candidate({self.id}, ({x:.2f},{y:.2f}), {self.first_name}, {self.last_name}, {self.scores})"
        return f"Candidate({self.id})"

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
