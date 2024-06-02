from dataclasses import dataclass, field, InitVar
from typing import List, Tuple
from math import sqrt, isclose

from .person import Person
from .candidate import Candidate


@dataclass(kw_only=True, eq=True)
class Elector(Person):
    """A class which represents an elector in the election."""

    candidates_ranked: List[Candidate] = field(
        default_factory=list, repr=False)
    """A ranking of candidates bases on elector's preferences. Decreasing order. 
    This list must contain all candidats who participate in the election. 
    """

    weight: int = 1
    """A weight of the elector. Strictly positive integer
        - If `weight` = 0, then an elector has made a delegation of his vote.   
        - If `weight` = 1, then an elector will vote for himself only.  
        - If `weight` > 1, then an elector has been chosen as a delegate and will vote for some other electors too.
    """

    knowledge: float = -1.0
    """A rate of knowledge of an elector on the election.
    If is given during an initialization, then it will be generated based on normal distribution.
    """

    knowledge_const: InitVar[Tuple[float, float]] = field(default=(0.5, 0.3), compare=False)
    """Parameters (mean, variance) for `knowledge` generation according to the normal distribution."""

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

    def __eq__(self, other):
        # Necessary to define manually because of Candidate
        if isinstance(other, self.__class__):
            return (super().__eq__(other) 
                    and other.candidates_ranked == self.candidates_ranked
                    and (isclose(other.knowledge, self.knowledge, rel_tol= 1e-4)) and other.weight == self.weight)
        return False

    def dist_from_one_cand(self, candidate: List[Candidate]) -> float:
        """Calculate the Euclidean distance between the position of an elector and a given candidate.

        Args:
            candidate (people.candidate.Candidate): A candidate with which the distance will be calculated.

        Returns:
            float: the Euclidean distance between an elector and a candidate.
        """

        x, y = self.position
        x_c, y_c = candidate.position
        return sqrt((x_c - x) ** 2 + (y_c - y) ** 2)

    def dist_from_cand(self, candidates: List[Candidate]) -> List[float]:
        """Calculate a list of Euclidean distances between elector and candidats. 

        Args:
            candidates (List[people.candidate.Candidate]): A list of candidates.

        Returns:
            List[float] : A list of the Euclidean distances.
        """

        distances = []
        for candidate in candidates:
            distances.append(self.dist_from_one_cand(candidate))
        return distances

    def pos_to_rank(self, candidates: List[Candidate]) -> List[Candidate]:
        """Rank candidates bases on preferences of an elector, which are invers
        Classe les candidats en fonction des préférences d'un électeur,
        which are inversely proportional to the distance between an elector and the candidates.
        The further away the candidate is, the less preferred he will be. 
        Conversely the closer the candidate is, the more preferred he will be. 


        Args:
            candidate (List[people.candidate.Candidate]): A list of candidates.
        Returns:
            List[people.candidate.Candidate]: A ranking of candidates, from more to less preferred.
        """

        distances = self.dist_from_cand(candidates)
        ranking = [
            c for (c, _) in sorted(zip(candidates, distances), key=lambda t: t[1])
        ]
        return ranking

    def rank_candidates(self, candidates: List[Candidate]) -> None:
        """Fill an attribute `candidates_ranked` with the ranking of candidates (from more to less preferred).

        Args:
            candidates (List[people.candidate.Candidate]): A list of candidates.
        """

        self.candidates_ranked = self.pos_to_rank(candidates)
