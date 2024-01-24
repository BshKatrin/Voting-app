class Person:
    def __init__(self, position):
        self.position = position

    def getPosition(self) :
        return self.position

    def __str__(self):
        x, y = self.position
        return f"Person ({x:.2f}, {y:.2f})"

    def __repr__(self):
        return self.__str__()
