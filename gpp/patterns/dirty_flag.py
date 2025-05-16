class GameObject:
    """
    Represents a game object that uses a dirty flag to avoid unnecessary computation.
    """
    def __init__(self, x: float, y: float, name: str):
        self._x = x
        self._y = y
        self._name = name
        self._is_dirty = True
        self._cached_representation = ""

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        if self._x != value:
            self._x = value
            self._is_dirty = True

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        if self._y != value:
            self._y = value
            self._is_dirty = True
            
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if self._name != value:
            self._name = value
            self._is_dirty = True

    def get_representation(self) -> str:
        """
        Returns a string representation of the object.
        Recomputes it only if the object's state has changed.
        """
        print(f"Getting representation for {self._name}. Dirty: {self._is_dirty}")
        if self._is_dirty:
            # Simulate some expensive computation
            self._cached_representation = f"Object '{self._name}' at ({self._x}, {self._y})"
            self._is_dirty = False
            print(f"Recomputed representation for {self._name}")
        return self._cached_representation

    def is_dirty(self) -> bool:
        """Returns the current state of the dirty flag."""
        return self._is_dirty
