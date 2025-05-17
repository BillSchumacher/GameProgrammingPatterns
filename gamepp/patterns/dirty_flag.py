class GameObject:
    """
    Represents a game object that uses a dirty flag to avoid unnecessary computation.
    Supports a hierarchical scene graph where transforms are relative to a parent.
    """

    def __init__(
        self, x: float, y: float, name: str, parent: "GameObject | None" = None
    ):
        self._local_x = x
        self._local_y = y
        self._name = name

        self._parent: "GameObject | None" = None  # Set via property to handle links
        self._children: list["GameObject"] = []

        self._cached_representation = ""
        self._cached_world_x: float = 0.0
        self._cached_world_y: float = 0.0

        # Dirty flag for the string representation itself
        self._is_dirty = True
        # Dirty flag for the world transform calculation
        self._is_world_transform_dirty = True

        self.parent = parent  # Use setter to establish initial parent link

    @property
    def local_x(self) -> float:
        return self._local_x

    @local_x.setter
    def local_x(self, value: float) -> None:
        if self._local_x != value:
            self._local_x = value
            self._mark_transform_dirty()

    @property
    def local_y(self) -> float:
        return self._local_y

    @local_y.setter
    def local_y(self, value: float) -> None:
        if self._local_y != value:
            self._local_y = value
            self._mark_transform_dirty()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if self._name != value:
            self._name = value
            # Only the representation is dirty, not necessarily the transform
            if not self._is_dirty:
                self._is_dirty = True

    @property
    def parent(self) -> "GameObject | None":
        return self._parent

    @parent.setter
    def parent(self, new_parent: "GameObject | None") -> None:
        if self._parent is new_parent:
            return

        if self._parent:
            self._parent._remove_child(self)

        self._parent = new_parent

        if self._parent:
            self._parent._add_child(self)

        # Changing parentage dirties the transform
        self._mark_transform_dirty()

    def _add_child(self, child: "GameObject") -> None:
        if child not in self._children:
            self._children.append(child)

    def _remove_child(self, child: "GameObject") -> None:
        if child in self._children:
            self._children.remove(child)

    def _mark_transform_dirty(self) -> None:
        """Marks this object's transform as dirty and propagates to children."""
        if not self._is_world_transform_dirty:
            self._is_world_transform_dirty = True
            # If transform is dirty, representation is also dirty
            self._is_dirty = True
            for child in self._children:
                child._mark_transform_dirty()  # Recursive call
        elif (
            not self._is_dirty
        ):  # If world transform was already dirty, ensure representation is also marked
            self._is_dirty = True
            # Children would have been marked by the first call that set _is_world_transform_dirty

    def get_world_transform(self) -> tuple[float, float]:
        """
        Calculates and returns the object's world coordinates.
        Caches the result and recomputes only if the transform is dirty.
        """
        if self._is_world_transform_dirty:
            if self._parent:
                parent_world_x, parent_world_y = self._parent.get_world_transform()
                self._cached_world_x = parent_world_x + self._local_x
                self._cached_world_y = parent_world_y + self._local_y
            else:
                self._cached_world_x = self._local_x
                self._cached_world_y = self._local_y
            self._is_world_transform_dirty = False

        return self._cached_world_x, self._cached_world_y

    def get_representation(self) -> str:
        """
        Returns a string representation of the object, including world and local coordinates.
        Recomputes it only if the object's representation state has changed.
        """
        # Ensure world transform is up-to-date before generating representation
        world_x, world_y = self.get_world_transform()

        print(f"Getting representation for {self._name}. Dirty: {self._is_dirty}")
        if self._is_dirty:
            # Simulate some expensive computation
            self._cached_representation = f"Object '{self._name}' at world ({world_x:.2f}, {world_y:.2f}), local ({self._local_x:.2f}, {self._local_y:.2f})"
            self._is_dirty = False
            print(f"Recomputed representation for {self._name}")
        return self._cached_representation

    def is_dirty(self) -> bool:
        """Returns the current state of the representation's dirty flag."""
        return self._is_dirty
