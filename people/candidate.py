from copy import deepcopy
from dataclasses import dataclass, field, InitVar
from string import ascii_uppercase
from typing import Dict, Union, List, Tuple
from itertools import product
from .person import Person

from electoral_systems import RandomConstants


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

    dogmatism: float = -1.0
    opposition: float = -1.0
    dogmatism_const: InitVar[Tuple[float, float]] = RandomConstants.DEFAULT_VALUES[
        RandomConstants.DOGMATISM
    ]
    opposition_const: InitVar[Tuple[float, float]] = RandomConstants.DEFAULT_VALUES[
        RandomConstants.OPPOSITION
    ]

    # int -> 1 round, float -> Copeland, List -> N rounds
    scores: Dict[str, Union[int, float, List[int]]] = field(
        default_factory=dict, hash=False, compare=False
    )

    def __post_init__(self, dogmatism_const, opposition_const):
        if not self.first_name:
            self.first_name = next(generator_first_name)
        if not self.last_name:
            self.last_name = next(generator_last_name)

        if self.dogmatism < 0:
            mu, sigma = dogmatism_const
            self.dogmatism = Person.generate_parameter(
                mu=mu, sigma=sigma, lower_limit=0, upper_limit=1
            )
        if self.opposition:
            mu, sigma = opposition_const
            self.opposition = Person.generate_parameter(
                mu=mu, sigma=sigma, lower_limit=0, upper_limit=1
            )

    def __str__(self):
        x, y = self.position
        # return f"Candidate({self.id}, ({x:.2f},{y:.2f}), {self.first_name}, {self.last_name}, {self.scores})"
        # return f"Candidate({self.id}, {self.first_name} {self.last_name}, domgat:{self.dogmatism:.2f}, oppos:{self.opposition:.2f})"
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

    # For polls. Move candidate to the average of the given positions
    def move_to_avg(self, positions, travel_dist):
        sum_x, sum_y = 0, 0
        for x, y in positions:
            sum_x, sum_y = sum_x + x, sum_y + y
        x_goal, y_goal = sum_x / len(positions), sum_y / len(positions)

        # print(self, f"{x_curr:.2f}, {y_curr:.2f}")
        self.move_to_point((x_goal, y_goal), travel_dist)

    def move_to_point(self, position_goal, travel_dist):
        x_curr, y_curr = self.position
        x_goal, y_goal = position_goal

        # Move towards x_goal
        x_curr += (x_goal - x_curr) * travel_dist
        y_curr += (y_goal - y_curr) * travel_dist

        self.position = (x_curr, y_curr)
