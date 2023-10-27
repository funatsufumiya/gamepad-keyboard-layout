class Singleton(type):
    """
    This is a metaclass for creating singletons.
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        """
        This method is called when an instance of the class is created.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        
        return cls._instances[cls]