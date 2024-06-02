from dataclasses import dataclass, field
from numpy.random import normal
from numpy import clip
from math import isclose

# For docs generation only
__pdoc__ = {'normal':False}

@dataclass(kw_only=True)
class Person:
    """A class which encapsulates the commun data between candidate and elector."""

    id: int = field(compare=False)
    """An person's identifier. Should by unique."""

    position: tuple[float, float] = field(compare=False)
    """A position on the political map. Coordinates should be bounded between -1 and 1."""

    
    @staticmethod
    def generate_parameter(mu: float, sigma: float, lower_limit: float, upper_limit: float) -> float:
        """Generate a paramater according to the normal distribution and bounded between given limits.

        Args:
            mu (float): A mean of the normal distribution.
            sigma (float): A variance of the normdal distribution. A strictly positive float.
            lower_limit (float): A lower limit of the parameter.
            upper_limit (float): An upper limit of the parameter.

        Returns:
            float: A generated parameter.
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
        # Necessary to define manually because of Candidate
        if isinstance(other, self.__class__):
            x, y = self.position
            x_o, y_o = other.position
            return (other.id == self.id and isclose(x, x_o, rel_tol=1e-4) and isclose(y, y_o, rel_tol=1e-4))
        return False