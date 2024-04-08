class IdIterator:
    def __init__(self, start):
        self.start = start
        self.current = self.start

    def __iter__(self):
        return self

    def __next__(self):
        id = self.current
        self.current += 1
        return id

    def restart(self):
        self.current = self.start
