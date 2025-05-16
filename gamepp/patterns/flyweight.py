from abc import ABC, abstractmethod
from typing import Dict, Any


class Flyweight(ABC):
    """
    The Flyweight interface declares a method for accepting extrinsic state.
    """

    @abstractmethod
    def operation(self, extrinsic_state: Any) -> None:
        pass


class ConcreteFlyweight(Flyweight):
    """
    The ConcreteFlyweight implements the Flyweight interface and
    adds storage for intrinsic state, if any.
    """

    def __init__(self, intrinsic_state: Any):
        self._intrinsic_state = intrinsic_state

    def operation(self, extrinsic_state: Any) -> None:
        print(
            f"ConcreteFlyweight: Intrinsic State = {self._intrinsic_state}, Extrinsic State = {extrinsic_state}"
        )


class FlyweightFactory:
    """
    The FlyweightFactory creates and manages flyweight objects.
    It ensures that flyweights are shared correctly. When the client
    requests a flyweight, the factory either returns an existing
    instance or creates a new one, if it doesn't exist yet.
    """

    _flyweights: Dict[Any, Flyweight] = {}  # Allow Any type for keys (str or tuple)

    def __init__(self, initial_flyweights: Dict[Any, Any]):
        for (
            _,
            value,
        ) in initial_flyweights.items():
            flyweight_key = self.get_key(value)
            if flyweight_key not in self._flyweights:
                self._flyweights[flyweight_key] = ConcreteFlyweight(value)

    def get_key(self, state: Any) -> Any:  # Return type is now Any
        """
        Returns a key for the Flyweight.
        Uses tuple directly if state is a tuple, otherwise generates a string key.
        """
        if isinstance(state, tuple):
            return state  # Use tuple directly as a key
        elif isinstance(state, dict):
            # Create a sorted tuple of items, then join to a string
            # Example: {'y': 20, 'x': 10} -> "x:10|y:20"
            return "|".join(f"{k}:{v}" for k, v in sorted(state.items()))
        # Fallback for other types (e.g. simple strings, numbers, or other objects)
        return str(state)

    def get_flyweight(self, shared_state: Any) -> Flyweight:
        """
        Returns an existing Flyweight with a given state or creates a new one.
        """
        key = self.get_key(shared_state)

        if key not in self._flyweights:
            print("FlyweightFactory: Can't find a flyweight, creating new one.")
            self._flyweights[key] = ConcreteFlyweight(shared_state)
        else:
            print("FlyweightFactory: Reusing existing flyweight.")

        return self._flyweights[key]

    def list_flyweights(self) -> None:
        count = len(self._flyweights)
        print(f"FlyweightFactory: I have {count} flyweights:")
        for key in self._flyweights.keys():
            print(key)
