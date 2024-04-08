from dataclasses import dataclass, field
from numpy.random import normal
from numpy import clip


@dataclass(kw_only=True, eq=True)
class Person:
    id: int = field(compare=False)
    position: tuple[float, float] = field(compare=False)

    # Generate parameters based on Gauss normal distribution
    # Confine generated parameter between lower and upper limits
    @staticmethod
    def generate_parameter(mu, sigma, lower_limit, upper_limit):
        max_iteration = 10
        param = normal(mu, sigma)
        while param < lower_limit or param > upper_limit and max_iteration:
            param = normal(mu, sigma)
            max_iteration -= 1

        # If value is still out of border, otherwise eternal loop
        param = clip(param, lower_limit, upper_limit)
        return param

    def get_position(self):
        return self.position

    def __str__(self):
        x, y = self.position
        return f"{self.__class__.__name__}({self.id}, ({x:.2f}, {y:.2f}))"

    def __repr__(self):
        return self.__str__()
