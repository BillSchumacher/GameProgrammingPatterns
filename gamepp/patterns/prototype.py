from abc import ABC, abstractmethod


class Prototype(ABC):
    """
    The Prototype interface declares a cloning method.

    Useful for making spawners or factories that can create new instances
    of a class without knowing the exact class type.
    """

    @abstractmethod
    def clone(self):
        """
        Returns a clone of the prototype.
        """
        pass
