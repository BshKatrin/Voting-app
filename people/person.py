from dataclasses import dataclass, field
from itertools import count
from random import uniform
from numpy.random import normal


@dataclass(kw_only=True, eq=True)
class Person:
    def gen_rand_position():
        return (uniform(-1, 1), uniform(-1, 1))

    id: int = field(default_factory=count().__next__, compare=False)
    position: tuple[float, float] = field(
        default_factory=gen_rand_position, compare=False
    )

    # Generate parameters based on Gauss normal distribution
    # Confine generated parameter between lower and upper limits
    @staticmethod
    def generate_parameter(mu, sigma, lower_limit, upper_limit):
        param = normal(mu, sigma)
        while param < lower_limit or param > upper_limit:
            param = normal(mu, sigma)
        return param

    def get_position(self):
        return self.position

    def __str__(self):
        x, y = self.position
        return f"{self.__class__.__name__}({self.id}, ({x:.2f}, {y:.2f}))"

    def __repr__(self):
        return self.__str__()
