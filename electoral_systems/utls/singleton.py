# Metaclass


# Si une instance n'existe pas -> la сreer et stocker dans _instances
# Sinon, retourner une instance
class Singleton(type):
    _instances = {}  # key : class, value : instance

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
