class IdIterator:
    """Un itérateur pour générer les IDs des candidats et des électeurs"""

    def __init__(self, start:int):
        """Un itérateur commence à partir du `start`.
        
        Args:
            start (int): Un nombre à partir duquel il faut commencer la génération.
        """

        self.start = start  # Premier nombre à générer
        self.current = self.start

    def __iter__(self):
        return self

    def __next__(self):
        id = self.current
        self.current += 1
        return id

    def restart(self):
        """Recommence une génération des nombres à partir du `start`"""
        self.current = self.start
