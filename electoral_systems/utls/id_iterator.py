class IdIterator:
    """Un itérateur pour générer les IDs des candidats et des électeurs."""

    def __init__(self, start):
        self.start = start  # Premier nombre à générer
        self.current = self.start

    def __iter__(self):
        return self

    def __next__(self):
        id = self.current
        self.current += 1
        return id

    def restart(self):
        """Recommencer une génération, i.e. le nombre suivant généré sera `self.start`"""
        self.current = self.start