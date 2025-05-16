"""
Implementation of the Type Object pattern.

This pattern allows for the creation of types dynamically at runtime,
without a fixed set of hardcoded classes. It involves two main components:
- TypeObject: Represents a logical type and stores shared data/behavior.
- TypedObject: Represents an instance of a type and stores instance-specific
             data, along with a reference to its TypeObject.
"""
import json
from typing import Optional, Dict

class TypeObject:
    """
    Represents a logical type.
    Stores data and behavior shared by all instances of this type.
    Supports inheritance from a parent TypeObject using copy-down delegation.
    """
    def __init__(self, name: str, health: int = 0, attack: Optional[str] = None, parent: Optional["TypeObject"] = None):
        self.name = name

        # Initialize with defaults or values from parent (copy-down)
        if parent:
            self._health = parent.health  # Use parent's resolved health
            self._attack = parent.attack  # Use parent's resolved attack
        else:
            self._health = 0  # Default health if no parent
            self._attack = None  # Default attack if no parent

        # Apply overrides from this type's explicit parameters
        # A health value of 0 means "inherit or use default", non-zero is an override.
        if health != 0:
            self._health = health
        # An attack value of None means "inherit or use default", non-None is an override.
        if attack is not None:
            self._attack = attack

    @property
    def health(self) -> int:
        """
        Gets the effective health for this type.
        This value is resolved at construction time (copy-down).
        """
        return self._health

    @property
    def attack(self) -> Optional[str]:
        """
        Gets the effective attack string for this type.
        This value is resolved at construction time (copy-down).
        """
        return self._attack

    def get_shared_behavior(self) -> str:
        """
        Returns a string describing the type's effective shared attributes (health and attack).
        """
        attack_description = self.attack if self.attack is not None else "Not specified"
        return f"Type '{self.name}': Health = {self.health}, Attack = '{attack_description}'"

    def new_object(self, instance_attribute: str) -> "TypedObject":
        """
        Factory method to create a new TypedObject of this type.
        """
        return TypedObject(self, instance_attribute)

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
        type_attack_description = self.type.attack if self.type.attack is not None else "Not specified"
        return (f"Instance of '{self.type.name}' "
                f"(Instance Data: '{self.instance_attribute}', "
                f"Type Health: {self.type.health}, Type Attack: '{type_attack_description}')")


def load_type_objects_from_data(breeds_data: Dict[str, Dict]) -> Dict[str, TypeObject]:
    """
    Loads TypeObject instances from a dictionary structure (e.g., parsed from JSON).
    Handles parent-child relationships for copy-down inheritance.
    It makes multiple passes to resolve dependencies.
    """
    type_objects_map: Dict[str, TypeObject] = {}
    
    # Use a list of tuples (name, config) to allow safe removal during iteration
    # and to handle processing order for dependencies.
    pending_configs = list(breeds_data.items())
    
    # Safeguard against infinite loops with malformed data (e.g. circular dependencies)
    max_passes = len(pending_configs) + 1 
    passes_count = 0
    
    while pending_configs and passes_count < max_passes:
        processed_in_this_pass = []
        for name, config in pending_configs:
            parent_name = config.get("parent")
            parent_obj: Optional[TypeObject] = None
            
            can_process_now = True
            if parent_name:
                if parent_name in type_objects_map:
                    parent_obj = type_objects_map[parent_name]
                else:
                    # Parent not yet processed, defer this item for a later pass
                    can_process_now = False
            
            if can_process_now:
                health = config.get("health", 0)  # Default to 0 (inherit/default)
                attack = config.get("attack")     # Default to None (inherit/default)
                
                type_obj = TypeObject(name=name, health=health, attack=attack, parent=parent_obj)
                type_objects_map[name] = type_obj
                processed_in_this_pass.append((name, config))
        
        if not processed_in_this_pass and pending_configs:
            # No progress was made in this pass, but items remain.
            # This indicates a cycle or a missing parent definition.
            remaining_names = [item[0] for item in pending_configs]
            raise ValueError(
                f"Could not resolve dependencies for: {remaining_names}. "
                "Check for circular dependencies or missing parent definitions."
            )

        # Remove successfully processed items from the pending list
        for item in processed_in_this_pass:
            if item in pending_configs:
                 pending_configs.remove(item)
        
        passes_count += 1

    if pending_configs:
        remaining_names = [item[0] for item in pending_configs]
        raise ValueError(
            f"Failed to process all breed definitions after {passes_count} passes. "
            f"Remaining: {remaining_names}. This might indicate an unresolvable circular dependency."
        )
            
    return type_objects_map


def load_types_from_json_string(json_string: str) -> Dict[str, TypeObject]:
    """
    Parses a JSON string and loads TypeObject instances using load_type_objects_from_data.
    """
    data = json.loads(json_string)
    return load_type_objects_from_data(data)

