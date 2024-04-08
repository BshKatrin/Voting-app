from copy import deepcopy
from dataclasses import dataclass, field, InitVar
from typing import Dict, Union, List, Tuple
from .person import Person


@dataclass(kw_only=True, unsafe_hash=True, eq=True, order=True)
class Candidate(Person):
    first_name: str = ""
    last_name: str = ""

    dogmatism: float = -1.0
    opposition: float = -1.0
    dogmatism_const: InitVar[Tuple[float, float]] = (0.5, 0.3)
    opposition_const: InitVar[Tuple[float, float]] = (0.5, 0.3)

    # int -> 1 round, float -> Copeland, List -> N rounds
    scores: Dict[str, Union[int, float, List[int]]] = field(
        default_factory=dict, hash=False, compare=False
    )

    def __post_init__(self, dogmatism_const, opposition_const):
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
        # return f"Candidate({self.id}, {self.first_name} {self.last_name})"
        return str(self.id)

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

        self.move_to_point((x_goal, y_goal), travel_dist)

    def move_to_point(self, position_goal, travel_dist):
        x_curr, y_curr = self.position
        x_goal, y_goal = position_goal

        # Move towards x_goal
        x_curr += (x_goal - x_curr) * travel_dist
        y_curr += (y_goal - y_curr) * travel_dist

        self.position = (x_curr, y_curr)
