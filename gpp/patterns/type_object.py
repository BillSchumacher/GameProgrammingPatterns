"""
Implementation of the Type Object pattern.

This pattern allows for the creation of types dynamically at runtime,
without a fixed set of hardcoded classes. It involves two main components:
- TypeObject: Represents a logical type and stores shared data/behavior.
- TypedObject: Represents an instance of a type and stores instance-specific
             data, along with a reference to its TypeObject.
"""

class TypeObject:
    """
    Represents a logical type.
    Stores data and behavior shared by all instances of this type.
    """
    def __init__(self, name: str, shared_attribute: str):
        self.name = name
        self.shared_attribute = shared_attribute

    def get_shared_behavior(self) -> str:
        """
        An example of a behavior shared by all objects of this type.
        """
        return f"Shared behavior from {self.name} type: {self.shared_attribute}"

class TypedObject:
    """
    Represents an instance of a specific type (defined by a TypeObject).
    Stores instance-specific data and a reference to its TypeObject.
    """
    def __init__(self, type_obj: TypeObject, instance_attribute: str):
        self._type_object = type_obj
        self.instance_attribute = instance_attribute

    @property
    def type(self) -> TypeObject:
        """
        Returns the TypeObject associated with this instance.
        """
        return self._type_object

    def get_instance_data(self) -> str:
        """
        Returns instance-specific data.
        """
        return self.instance_attribute

    def perform_shared_action(self) -> str:
        """
        Delegates to the TypeObject for shared behavior.
        """
        return self._type_object.get_shared_behavior()

    def __str__(self) -> str:
        return f"Instance of {self.type.name} (Instance: {self.instance_attribute}, Shared: {self.type.shared_attribute})"

