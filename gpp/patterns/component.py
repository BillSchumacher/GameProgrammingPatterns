"""
Component Pattern Implementation
"""

class Component:
    """Base class for components."""
    def __init__(self):
        self._entity = None

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, entity):
        self._entity = entity

    def update(self):
        """Update method for the component, to be overridden by subclasses."""
        pass

class Entity:
    """A container for components."""
    def __init__(self):
        self._components = {}

    def add_component(self, component_instance):
        """Adds a component to the entity."""
        component_class = type(component_instance)
        if component_class in self._components:
            raise ValueError(f"Component {component_class.__name__} already exists on this entity.")
        self._components[component_class] = component_instance
        component_instance.entity = self
        return component_instance # Return instance for chaining or direct use

    def get_component(self, component_class):
        """Retrieves a component from the entity."""
        return self._components.get(component_class)

    def remove_component(self, component_class):
        """Removes a component from the entity."""
        if component_class in self._components:
            component_instance = self._components.pop(component_class)
            component_instance.entity = None
            return True
        return False

    def has_component(self, component_class):
        """Checks if the entity has a specific component."""
        return component_class in self._components

    def update_components(self):
        """Calls the update method on all components."""
        for component in self._components.values():
            if hasattr(component, 'update') and callable(component.update):
                component.update()

# Example Concrete Components
class PositionComponent(Component):
    """Stores position data."""
    def __init__(self, x=0, y=0):
        super().__init__()
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def __str__(self):
        return f"PositionComponent(x={self.x}, y={self.y})"

class HealthComponent(Component):
    """Manages health data."""
    def __init__(self, health=100):
        super().__init__()
        self.health = health

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount

    def __str__(self):
        return f"HealthComponent(health={self.health})"

class InputComponent(Component):
    """Handles input and can trigger actions on other components."""
    def __init__(self):
        super().__init__()
        self.last_command = None

    def process_input(self, command):
        self.last_command = command
        # Example: if entity has a position component, move it
        if command == "move_left":
            pos_comp = self.entity.get_component(PositionComponent)
            if pos_comp:
                pos_comp.move(-1, 0)
        elif command == "move_right":
            pos_comp = self.entity.get_component(PositionComponent)
            if pos_comp:
                pos_comp.move(1, 0)

    def update(self):
        """Example update: print last command or perform continuous action."""
        if self.last_command:
            # In a real game, this might be where continuous actions are processed
            # print(f"InputComponent updated, last command: {self.last_command}")
            pass

    def __str__(self):
        return f"InputComponent(last_command='{self.last_command}')"
