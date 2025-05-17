"""
Object Pool Pattern

Defines a pool class that maintains a collection of reusable objects.
Each object supports an “in use” query to tell if it is currently “alive”.
When the pool is initialized, it creates the entire collection of objects up front
and initializes them all to the “not in use” state.
When a new object is needed, the pool is asked for one. It finds an available
object, marks it as “in use”, and returns it. When the object is no longer
needed, it is set back to the “not in use” state by resetting it.
This way, objects can be acquired and released without needing to allocate
memory or other resources repeatedly.
"""

from typing import TypeVar, Generic, Type, List, Optional, Dict, Any

# Define a TypeVar for the PooledObject subclass.
# 'bound=PooledObject' ensures that T_PooledObject is a subclass of PooledObject.
# However, to define PooledObject first, we use a forward reference string.
T_PooledObject = TypeVar("T_PooledObject", bound="PooledObject")


class PooledObject:
    """
    Base class for objects that can be managed by an ObjectPool.
    Supports an "in use" query and a reset mechanism.

    Subclasses should override the `reset` method to clear their specific state
    and call `super().reset()`.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes the PooledObject.
        Sets the initial state to not in use.
        Accepts *args and **kwargs to be flexible for subclasses, though this
        base class does not use them directly.
        """
        self._in_use: bool = False
        # Subclasses can initialize other attributes here

    def is_in_use(self) -> bool:
        """Checks if the object is currently in use."""
        return self._in_use

    def _set_in_use_status(self, status: bool) -> None:
        """
        Internal method to set the in_use status.
        This is typically called by the ObjectPool when acquiring an object,
        or by the object's own reset method.
        """
        self._in_use = status

    def reset(self) -> None:
        """
        Resets the object to its initial state and marks it as not in use.
        This method MUST be overridden by subclasses to reset their specific state
        if they have any. Subclasses should also call `super().reset()`.
        The base implementation only marks the object as not in use.
        """
        self._set_in_use_status(False)
        # Example for subclasses:
        # super().reset()
        # self.custom_data = None
        # self.position = (0,0)


class ObjectPool(Generic[T_PooledObject]):
    """
    Manages a collection of reusable PooledObject instances.

    This class creates a fixed number of objects upfront and allows them
    to be acquired and released, aiming to reduce the overhead of
    creating and destroying objects frequently.
    """

    def __init__(
        self,
        object_class_to_pool: Type[T_PooledObject],
        pool_size: int,
        *object_init_args: Any,
        **object_init_kwargs: Any,
    ) -> None:
        """
        Initializes the object pool.

        Args:
            object_class_to_pool: The class of the objects to pool.
                                  Must be a subclass of PooledObject.
            pool_size: The number of objects to create and manage in the pool.
            *object_init_args: Positional arguments to pass to the constructor
                               of each pooled object.
            **object_init_kwargs: Keyword arguments to pass to the constructor
                                  of each pooled object.
        """
        if not isinstance(pool_size, int) or pool_size <= 0:
            raise ValueError("Pool size must be a positive integer.")

        self._pool: List[T_PooledObject] = []
        for _ in range(pool_size):
            # Create a new instance of the object
            obj = object_class_to_pool(*object_init_args, **object_init_kwargs)
            if not isinstance(obj, PooledObject):
                raise TypeError(
                    f"Class {object_class_to_pool.__name__} must inherit from PooledObject."
                )
            # Ensure it's in the "not in use" state and properly reset initially
            obj.reset()
            self._pool.append(obj)

    def acquire_object(self) -> Optional[T_PooledObject]:
        """
        Acquires an available object from the pool.

        The acquired object is marked as "in use". If the object has specific
        state that needs to be configured after acquisition, the caller is
        responsible for that.

        Returns:
            A PooledObject instance from the pool, or None if no objects are
            currently available.
        """
        for obj in self._pool:
            if not obj.is_in_use():
                obj._set_in_use_status(True)  # Mark as "in use"
                return obj
        return None  # Pool is exhausted

    def release_object(self, obj: T_PooledObject) -> None:
        """
        Returns an object to the pool.

        The object is marked as "not in use" by calling its `reset()` method,
        which should also revert its state to be ready for reuse.

        Args:
            obj: The PooledObject instance to release back to the pool.

        Raises:
            ValueError: If the object being released does not belong to this pool
                        or is not a PooledObject instance.
        """
        if not isinstance(obj, PooledObject):
            raise ValueError("Object being released is not a PooledObject instance.")

        # Check if the object is one of the instances managed by this pool.
        # This check is by identity.
        if obj in self._pool:
            if not obj.is_in_use():
                # Optionally, handle or log releasing an already available object
                # print(f"Warning: Object {obj} was already available in the pool.")
                pass  # Or raise an error if this is an invalid state
            obj.reset()  # Reset state and mark as not in use
        else:
            raise ValueError("Object being released does not belong to this pool.")

    def get_pool_info(self) -> Dict[str, int]:
        """
        Provides information about the current state of the object pool.

        Returns:
            A dictionary containing the total number of objects,
            the number of used objects, and the number of available objects.
        """
        total_objects = len(self._pool)
        used_objects = sum(1 for obj in self._pool if obj.is_in_use())
        available_objects = total_objects - used_objects
        return {
            "total_objects": total_objects,
            "used_objects": used_objects,
            "available_objects": available_objects,
        }
