from dataclasses import dataclass, field
from itertools import count
from random import uniform


@dataclass(kw_only=True, eq=True)
class Person:
    def gen_rand_position():
        return (uniform(-1, 1), uniform(-1, 1))

    id: int = field(default_factory=count().__next__, compare=False)
    position: (float, float) = field(default_factory=gen_rand_position, compare=False)

    def get_position(self):
        return self.position

    def __str__(self):
        x, y = self.position
        return f"{self.__class__.__name__}({self.id}, ({x:.2f}, {y:.2f}))"

    def __repr__(self):
        return self.__str__()
