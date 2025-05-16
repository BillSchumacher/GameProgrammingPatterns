"""
Component Pattern Implementation
"""

class Component:
    """Base class for components."""
    def __init__(self):
        pass

    def update(self, entity: "Entity"):
        """Update method for the component, to be overridden by subclasses."""
        pass

class Entity:
    """A container for components."""
    def __init__(self):
        self._components = {}

    def add_component(self, component_instance: Component):
        """Adds a component to the entity."""
        component_class = type(component_instance)
        if component_class in self._components:
            raise ValueError(f"Component {component_class.__name__} already exists on this entity.")
        self._components[component_class] = component_instance
        return component_instance # Return instance for chaining or direct use

    def get_component(self, component_class: Component):
        """Retrieves a component from the entity."""
        return self._components.get(component_class)

    def remove_component(self, component_class: Component):
        """Removes a component from the entity."""
        if component_class in self._components:
            self._components.pop(component_class)
            return True
        return False

    def has_component(self, component_class: Component):
        """Checks if the entity has a specific component."""
        return component_class in self._components

    def update_components(self):
        """Calls the update method on all components."""
        for component in self._components.values():
            component.update(self)


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

    def process_input(self, entity, command): # Added entity argument
        self.last_command = command
        # Example: if entity has a position component, move it
        if command == "move_left":
            pos_comp = entity.get_component(PositionComponent) # Use passed entity
            if pos_comp:
                pos_comp.move(-1, 0)
        elif command == "move_right":
            pos_comp = entity.get_component(PositionComponent) # Use passed entity
            if pos_comp:
                pos_comp.move(1, 0)

    def update(self, entity): # Added entity argument
        """Example update: print last command or perform continuous action."""
        if self.last_command:
            # In a real game, this might be where continuous actions are processed
            # print(f"InputComponent updated using {entity}, last command: {self.last_command}")
            pass

    def __str__(self):
        return f"InputComponent(last_command='{self.last_command}')"

class RenderComponent(Component):
    """Handles rendering logic."""
    def __init__(self):
        super().__init__()
        self.render_data = None

    def render(self, entity):
        # Example render logic
        pos_comp = entity.get_component(PositionComponent)
        if pos_comp:
            self.render_data = f"Rendering at ({pos_comp.x}, {pos_comp.y})"
            print(self.render_data)

    def update(self, entity):
        """Example update: call render method."""
        self.render(entity)


class PlayerEntity(Entity):
    """A specific type of entity representing a player."""
    def __init__(self):
        super().__init__()
        self.add_component(PositionComponent())
        self.add_component(HealthComponent())
        self.add_component(InputComponent())
        self.add_component(RenderComponent())
    
    def update(self):
        """Update all components of the player entity."""
        super().update_components()
        # Additional player-specific updates can be added here
        # For example, checking for game over conditions based on health
        health_comp = self.get_component(HealthComponent)
        if health_comp and health_comp.health <= 0:
            print("Game Over! Player has no health left.")


class AlternateEntity:

    def __init__(self):
        self._input_component = InputComponent()
        self._position_component = PositionComponent()
        self._health_component = HealthComponent()
        self._render_component = RenderComponent()
    
    def update(self):
        """Update all components of the alternate entity."""
        self._input_component.update(self)
        self._position_component.update(self)
        self._health_component.update(self)
        self._render_component.update(self)