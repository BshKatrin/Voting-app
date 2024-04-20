from dataclasses import dataclass, field
from numpy.random import normal
from numpy import clip
from math import isclose

# Uniquement pour la génération des docs
__pdoc__ = {'normal':False}

@dataclass(kw_only=True)
class Person:
    """Une classe Person avec son identifiant `id` et sa position sur la carte politique `position`.
    Encapsule les données communes des candidats et des électeurs."""

    id: int = field(compare=False)
    """Un identifiant d'une personne."""

    position: tuple[float, float] = field(compare=False)
    """Une position sur la carte politique. Chaque coordonée est bornée entre -1 et 1"""

    
    @staticmethod
    def generate_parameter(mu: float, sigma: float, lower_limit: float, upper_limit: float) -> float:
        """Génére un paramètre basé sur la distribution normale et confiné entre des limites données.

        Args:
            mu (float): La moyenne de la distribution normale.
            sigma (float): L'écart type de la distribution normale. Un réel strictement positif.
            lower_limit (float): La limite inférieure pour le paramètre. 
            upper_limit (float): La limite supérieure pour le paramètre.

        Returns:
            float: Le paramètre généré.
        """

        max_iteration = 10
        param = normal(mu, sigma)
        while param < lower_limit or param > upper_limit and max_iteration:
            param = normal(mu, sigma)
            max_iteration -= 1

        # If value is still out of border, otherwise eternal loop
        param = clip(param, lower_limit, upper_limit)
        return param

    def __str__(self):
        x, y = self.position
        return f"{self.__class__.__name__}({self.id}, ({x:.2f}, {y:.2f}))"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # Nécessaire de définir manuellemnt à cause du Candidate
        if isinstance(other, self.__class__):
            x, y = self.position
            x_o, y_o = other.position
            return (other.id == self.id and isclose(x, x_o, rel_tol=1e-4) and isclose(y, y_o, rel_tol=1e-4))
        return False