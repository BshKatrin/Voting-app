from copy import deepcopy
from dataclasses import dataclass, field, InitVar
from typing import Dict, Union, List, Tuple, Optional

from numpy import clip
from .person import Person


@dataclass(kw_only=True, unsafe_hash=True, eq=True, order=True)
class Candidate(Person):
    """A class which represents a candidate in the election. **A tuple (first_name, last_name) should be unique**.
    Candidates are compared by full name only."""

    first_name: str = field(default="", hash=True, compare=True)
    """Candidate's first name."""

    last_name: str = field(default="", hash=True, compare=True)
    """Candidate's last name."""

    dogmatism: float = field(default=-1.0, hash=True, compare=False)
    """A parameter for polls. Between 0 and 1. The higher the level of dogmatism,
    the more certain the candidate is of his political stance, and it is unlikely that he will decide to change it.
    Conversely, the lower the level of dogmatism, the more likely it is that the candidate will decide to change
    his political position, to abandon the election and/or to form an alliance with another candidate with a similiar political views.  
    If the level of dogmatism is not given during initialization, it will be generated according to a the normal distribution 
    with parameters stored in `dogmatism_const`.
    """

    opposition: float = field(default=-1.0, hash=True, compare=False)
    """A parameter for polls. Between 0 and 1. The higher the level of opposition,
    the more it is unlikely that the candidate will decide to get closer to the winner of the election.
    Conversely, the lower the level of opposition, the more likely it is that the candidate will decide
    to get closer the winner.  
    If the level of dogmatism is not given during initialization, it will be generated according to a the normal distribution 
    with parameters stored in `opposition_const`.
    """

    dogmatism_const: InitVar[Tuple[float, float]] = field(
        default=(0.5, 0.3), compare=False)
    """Parameters (mean, variance) to generate the level of dogmatism according to the normal distribution."""

    opposition_const: InitVar[Tuple[float, float]] = field(
        default=(0.5, 0.3), compare=False)
    """Parameters (mean, variance) to generate the level of opposition according to the normal distribution."""

    # int -> 1 round, float -> Copeland, List -> N rounds
    scores: Dict[str, Union[int, float, List[int]]] = field(
        default_factory=dict, hash=False, compare=False
    )
    """A dictionary of scores for each voting rule chosen in the election.
    Types of values:   
        - int: one round, Condorcet, Simpson voting rules  
        - float: Copeland method  
        - List[int]: multi rounds voting rules  
    """

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
        
    def init_score(self, voting_rule: str, new_score: Union[int, float], list_type: Optional[bool] = False) -> None:
        """Initialize `scores[voting_rule]` with `new_score`

        Args:
            voting_rule (str): A constant related to the voting rule.
            new_score (Union[int, float]): A new score.
            list_type (Optional[bool]): Must be `True` if the type of `new_score` is `List`.
            In the case, `deepcopy` will be used for initialization. If `False`, initialization is done by simple assignement.
            Default = `False`.
        """

        if not list_type:
            self.scores[voting_rule] = new_score
        else:
            self.scores[voting_rule] = deepcopy(new_score)

    def add_score(self, voting_rule: str, score: Union[int, float]) -> None:
        """Add score `score` to the already existing score `scores[voting_rule]`.
        Used only for one round and Condorcet-based voting rules.

        Args:
            voting_rule (str): A constant related to one round or Condorcet-based voting rule.
            score (Union[int, float]): A score to add.
        """

        if voting_rule not in self.scores:
            self.init_score(voting_rule, 0)
        self.scores[voting_rule] += score

    def add_score_round(self, voting_rule: str, score: Union[int, float], round: int) -> None:
        """Add score `score` to the already existing score `scores[voting_rule]` in the round `round`.
        Used only for multi-round voting rules.

        Args:
            voting_rule (str): A constant related to one round or Condorcet-based voting rule.
            score (Union[int, float]): A score to add. 
            round (int): A round of the voting rule. Starts from 0. 

        Raises:
            IndexError: If `round` is bigger than the initialized number of rounds.
        """

        if voting_rule not in self.scores:
            self.init_score(voting_rule, [0] * round, True)
        if round >= len(self.scores[voting_rule]):
            raise IndexError
        self.scores[voting_rule][round] += score

    def move_to_avg(self, positions: List[tuple[float, float]], travel_dist: float) -> None:
        """Change candidate's position by getting closer to the mean of given positions stored in `positions`.
        The rate of change is determined by `travel_dist`.

        Args:
            positions (List[tuple[float, float]]): A list of positions from which the mean will be calculated.
            travel_dist (float): A distance at which the candidate will move. Should be bounded between 0 and 1.
        """

        sum_x, sum_y = 0, 0
        for x, y in positions:
            sum_x, sum_y = sum_x + x, sum_y + y
        x_goal, y_goal = sum_x / len(positions), sum_y / len(positions)

        self.move_to_point((x_goal, y_goal), travel_dist)

    def move_to_point(self, position_goal, travel_dist) -> None:
        """Change candidate's position by getting closer to the position `position_goal`. 
        The rate of change is determined by `travel_dist`. If coordinates of new position are beyond map bounds,
        it will by cut from -1 to 1.

        Args:
            position_goal (tuple[float, float]): A position to which the candidate will move closer.
                Coordinates should be between -1 and 1. 
            travel_dist: A distance at which the candidate will move. Should by bounded between 0 and 1.
        """

        x_curr, y_curr = self.position
        x_goal, y_goal = position_goal

        # Move towards x_goal, y_goal
        x_curr += (x_goal - x_curr) * travel_dist
        y_curr += (y_goal - y_curr) * travel_dist
        x_curr = clip(x_curr, -1, 1)
        y_curr = clip(y_curr, -1, 1)
        self.position = (x_curr, y_curr)
