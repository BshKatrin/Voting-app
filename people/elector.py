from dataclasses import dataclass, field, InitVar
from typing import List, Tuple
from math import sqrt

from .person import Person
from .candidate import Candidate


@dataclass(kw_only=True, eq=False)
class Elector(Person):
    """Une classe permettant de représenter un électeur dans une élection."""
    candidates_ranked: List[Candidate] = field(
        default_factory=list, repr=False)
    """
    Un classement des candidats selon les préférences d'un électeur dans l'ordre décroissant.
    Cette liste doit contenir tous les candidats qui participent dans une élection.
    """
    weight: int = 1
    """
    Un poids d'un électeur, un entier positive.
        - Si `weight` = 0, alors un électeur a fait un délégation
        - Si `weight` = 1, alors un électeur vote pour lui-même.
        - Si `weight` > 1, alors un électeur a été choisie comme un délégataire
    """
    knowledge: float = -1.0
    """
    Un taux des connaissances d'un électeur sur une élection.
    S'il n'était pas donné lors d'initialisation, alors `knowledge` est généré selon une loi normale
    """
    knowledge_const: InitVar[Tuple[float, float]] = (0.5, 0.3)
    """Des paramètres (moyenne, écart-type) pour une génération de `knowledge` selon une loi normale"""

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

    def dist_from_one_cand(self, candidate):
        """Calculer la distance euclidienne entre la position d'un électeur et celle d'un candidat donné.

        Args:
            candidate (people.candidate.Candidate): Le candidat avec lequel la distance sera calculée.

        Returns:
            float: La distance euclidienne entre un électeur et un candidat.
        """
        x, y = self.position
        x_c, y_c = candidate.position
        return sqrt((x_c - x) ** 2 + (y_c - y) ** 2)

    def dist_from_cand(self, candidates):
        """Calculer une liste des distances euclidiennes entre un électeur et des candidats.

        Args:
            candidates (List[people.candidate.Candidate]) : Une liste des candidats avec lesquels les distances seront calculées.

        Returns:
            List[float] : Une liste des distances euclidiennes.
        """
        distances = []
        for candidate in candidates:
            distances.append(self.dist_from_one_cand(candidate))
        return distances

    # Calculate ranking from given position (x,y)
    def pos_to_rank(self, candidates):
        """Classer les candidats en fonction des préférences d'un électeur,
        qui sont inversement proportionnelles à la distance des candidats.
        Plus un candidat est éloigné, moins il est préféré par l'électeur,
        et inversement, moins un candidat est éloigné, plus il est préféré.

        Args:
            candidate (List[people.candidate.Candidate]): Une liste des candidats.
        Returns:
            List[people.candidate.Candidate]: Un classement des candidats, du plus préféré au moins préféré.
        """
        distances = self.dist_from_cand(candidates)
        ranking = [
            c for (c, _) in sorted(zip(candidates, distances), key=lambda t: t[1])
        ]
        return ranking

    def rank_candidates(self, candidates):
        """Remplir un attribut `candidates_ranked` avec un classement des candidats selon leurs éloignement d'un électeur.

        Args:
            candidates (List[people.candidate.Candidate]): Une liste des candidats.
        """
        self.candidates_ranked = self.pos_to_rank(candidates)
