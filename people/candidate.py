from copy import deepcopy
from dataclasses import dataclass, field, InitVar
from typing import Dict, Union, List, Tuple, Optional

from numpy import clip
from .person import Person


@dataclass(kw_only=True, unsafe_hash=True, eq=True, order=True)
class Candidate(Person):
    """Une classe permettant de représenter un candidat dans une élection.
    *Une couple (first_name, last_name) doit être unique*."""

    first_name: str = field(default="", hash=True, compare=True)
    """Un prénom d'un candidat."""

    last_name: str = field(default="", hash=True, compare=True)
    """Un nom d'un candidat."""

    dogmatism: float = field(default=-1.0, hash=True, compare=False)
    """Sondages : Plus le taux de dogmatisme est élevé, plus le candidat est sûr de sa position politique
    et il est peu probable qu'il décide de la changer, et inversement, moins le taux de dogmatisme est élevé,
    plus il est probable que le candidat décide de changer sa position politique
    ou d'abandonner une élection et/ou former une alliance.  
    Si le taux de dogmatisme n'est pas donné lors de l'initialisation, il est généré selon la distribution normale 
    à l'aide de `dogmatism_const`.
    """

    opposition: float = field(default=-1.0, hash=True, compare=False)
    """Sondages : Plus le taux d'opposition est élevé, moins il est probable que le candidat décide
    de changer sa position politique en s'approchant le gagnant d'une élection, et inversement, 
    moins le taux d'opposition est élevé, plus il est probable que le candidat décide de s'approcher 
    le gagnant d'une élection.  
    Si le taux d'opposition n'est pas donné lors de l'initialisation, il est généré selon la distribution normale
    à l'aide de `opposition_const`.
    """

    dogmatism_const: InitVar[Tuple[float, float]] = field(
        default=(0.5, 0.3), compare=False)
    """Des paramètres (moyenne, écart-type) pour générer le taux de dogmatism selon la distribution normale."""

    opposition_const: InitVar[Tuple[float, float]] = field(
        default=(0.5, 0.3), compare=False)
    """Des paramètres (moyenne, écart-type) pour générer le taux d' opposition selon la distribution normale."""

    # int -> 1 round, float -> Copeland, List -> N rounds
    scores: Dict[str, Union[int, float, List[int]]] = field(
        default_factory=dict, hash=False, compare=False
    )
    """Un dictionnaire des scores pour chaque règle de vote utilisée lors d'une élection.  
    Les types selon les règles de vote:  
        - int: des règles de vote à 1 tour  
        - float: une règle de vote *Copeland*  
        - List[int]: des règles de vote à plusieurs tours  
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
        """Initialiser la case `scores[voting_rule]` avec `new_score`

        Args:
            voting_rule (str): La constante associée à une règle de vote.
            new_score (Union[int, float]): Le score avec lequel il faut d'initialiser la case.
            list_type (Optional[bool]): Doit être `True` si le type de `new_score` est `List` et il faut passer par `deepcopy`.
                Sinon, l'initialisation est faite par une affectation simple. Default = `False`.
        """

        if not list_type:
            self.scores[voting_rule] = new_score
        else:
            self.scores[voting_rule] = deepcopy(new_score)

    def add_score(self, voting_rule: str, score: Union[int, float]) -> None:
        """Ajouter le score `score` dans une case `scores[voting_rule]` vers le score déjà existant.
        Utiliser uniqument pour des règles de vote à un tour ou Condorcet-cohérentes.

        Args:
            voting_rule (str):  La constante associée à une règle de vote à un tour ou Condorcet-cohérente.
            score (Union(int, float)): Le score à ajouter.
        """

        if voting_rule not in self.scores:
            self.init_score(voting_rule, 0)
        self.scores[voting_rule] += score

    # Round commence a partir de 0
    def add_score_round(self, voting_rule: str, score: Union[int, float], round: int) -> None:
        """Ajouter le score `score` dans une tour `round` dans une case `scores[voting_rule]`.
        Utiliser uniquement pour des règles de vote à plusieurs tours.

        Args:
            voting_rule (str):  La constante associée à une règle de vote à plusieurs tours.
            score (Union[int, float]): Le score à ajouter.
            round (int): Le tour de la règle de vote. Commence à partir de 0.

        Raises:
            IndexError: Si `round` est plus grand que le nombre des tours initialisé.
        """

        if voting_rule not in self.scores:
            self.init_score(voting_rule, [0] * round, True)
        if round >= len(self.scores[voting_rule]):
            raise IndexError
        self.scores[voting_rule][round] += score

    def move_to_avg(self, positions: List[tuple[float, float]], travel_dist: float) -> None:
        """Changer la position d'un candidat en s'approchant la position moyenne des positions données.
        Le taux de changement de la position est déterminé par `travel_dist`.

        Args:
            positions (List[tuple[float, float]]): La liste des positions à partir de laquelle une position moyenne sera calculée.
            travel_dist (float): La distance à laquelle un candidat va bouger. Doit être bornée entre 0 et 1.
        """

        sum_x, sum_y = 0, 0
        for x, y in positions:
            sum_x, sum_y = sum_x + x, sum_y + y
        x_goal, y_goal = sum_x / len(positions), sum_y / len(positions)

        self.move_to_point((x_goal, y_goal), travel_dist)

    def move_to_point(self, position_goal, travel_dist) -> None:
        """Changer la position d'un candidat en s'approchant la position `position_goal`.
        Le taux de changement de la position est déterminé par `travel_dist`.
        Si les coordonnées de la nouvelle positions sont hors bornes, alors elles sont coupées de -1 à 1.

        Args:
            position_goal (tuple[float, float]): La position vers laquelle il faut s'approcher. Chaque coordonnée doit être borné
                entre -1 et 1.
            travel_dist: La distance à laquelle un candidat va bouger. Doit être bornée entre 0 et 1.
        """

        x_curr, y_curr = self.position
        x_goal, y_goal = position_goal

        # Move towards x_goal, y_goal
        x_curr += (x_goal - x_curr) * travel_dist
        y_curr += (y_goal - y_curr) * travel_dist
        x_curr = clip(x_curr, -1, 1)
        y_curr = clip(y_curr, -1, 1)
        self.position = (x_curr, y_curr)
