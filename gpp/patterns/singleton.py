"""Singleton, a generally terrible design pattern that is often misused.

Before using this pattern, consider if you really need a singleton."""


class SingletonMeta(type):
    """
    A metaclass for creating Singleton classes.
    Ensures that only one instance of a class is created.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Override the call behavior to control instance creation.
        If an instance of the class doesn't exist, create one; otherwise, return the existing instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """
    Base class for Singletons. Inherit from this class to make your class a Singleton.
    Example:
        class Logger(Singleton):
            def __init__(self, file_name="log.txt"):
                # __init__ will be called only once when the first instance is created.
                print(f"Logger initialized with {file_name}")
                self.file_name = file_name

            def log(self, message):
                print(f"Logging to {self.file_name}: {message}")

    # Usage:
    # logger1 = Logger()
    # logger2 = Logger("other_log.txt") # __init__ won't run again, file_name will remain "log.txt"
    # print(logger1 is logger2)  # True
    # logger1.log("This is a test.")
    """
    def __init__(self, *args, **kwargs):
        # The actual initialization logic should be in the subclass.
        # This __init__ in the base Singleton class is to allow subclasses to have their own __init__.
        # The metaclass ensures __init__ is called only once.
        pass
