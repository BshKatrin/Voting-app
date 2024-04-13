class Singleton(type):
    """Une metaclass pour une élection. But: partager les données entre plusieurs widgets de QT."""
    _instances = {}  # clé : class, valeur : instance

    def __call__(cls, *args, **kwargs):
        # Si une instance n'existe pas -> la сreer et stocker dans _instances. Sinon, retourner une instance
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
