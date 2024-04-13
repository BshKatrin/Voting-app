class NameIterator:
    """Un itérateur pour générer les prénoms et les noms des candidats. 
    Les chaînes de caractères sont générées de A à Z, après de AA à AZ, de BA à BZ etc."""

    def __init__(self):
        self.start = "A"
        self.nb_letters = 26  # dans un alphabet anglais
        self.current_ascii = [0]

    def __iter__(self):
        return self

    def __next__(self):
        name = "".join([chr(i + ord(self.start)) for i in self.current_ascii])
        self.increment()
        return name

    def increment(self):
        """Incrémente une lettre suivante à générer. """
        for i in range(len(self.current_ascii) - 1, -1, -1):
            if self.current_ascii[i] == self.nb_letters:
                # No places left
                if i == 0:
                    self.current_ascii.insert(0, 0)
                else:
                    # Start from beggining, increment next letters
                    self.current_ascii[i] = 0
            else:
                self.current_ascii[i] += 1
                break

    def restart(self):
        """Recommence une génération, i.e. la chaînes de caractères suivante sera 'A'"""
        self.current_ascii = [0]
