from typing import List, Protocol


class Entity(Protocol):
    """
    Represents an object in the game that has behavior to be updated each frame.
    """

    def update(self, dt: float) -> None:
        """
        Processes one frame of behavior for the entity.

        Args:
            dt: The time elapsed since the last frame, in seconds.
        """
        ...


class UpdateMethodManager:
    """
    Manages a collection of entities and updates them.
    """

    def __init__(self):
        self._entities: List[Entity] = []

    def add_entity(self, entity: Entity) -> None:
        """Adds an entity to be managed and updated."""
        if entity not in self._entities:
            self._entities.append(entity)

    def remove_entity(self, entity: Entity) -> None:
        """Removes an entity from management."""
        try:
            self._entities.remove(entity)
        except ValueError:
            # Entity not found, do nothing or log a warning
            pass

    def update_all(self, dt: float) -> None:
        """
        Updates all managed entities.

        Args:
            dt: The time elapsed since the last frame, in seconds.
        """
        for entity in self._entities:
            entity.update(dt)

    @property
    def entities(self) -> List[Entity]:
        """Returns a copy of the list of managed entities."""
        return list(self._entities)
