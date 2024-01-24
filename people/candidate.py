class Candidate(Person):
    def __init__(self, position):
        super().__init__(position)
        self.scores = dict()
