"""
Unit tests for the Component pattern.
"""
import unittest
from unittest import mock
from gamepp.patterns.component import Entity, Component, PositionComponent, HealthComponent, InputComponent

class TestComponentPattern(unittest.TestCase):
    """Tests the Component pattern implementation."""

    def test_entity_creation(self):
        """Test the creation of an Entity."""
        entity = Entity()
        self.assertIsNotNone(entity)
        self.assertEqual(len(entity._components), 0)

    def test_add_and_get_component(self):
        """Test adding and retrieving a component."""
        entity = Entity()
        pos_component = entity.add_component(PositionComponent(10, 20))
        self.assertIsInstance(pos_component, PositionComponent)
        self.assertEqual(pos_component.x, 10)
        self.assertEqual(pos_component.y, 20)

        retrieved_pos = entity.get_component(PositionComponent)
        self.assertIs(retrieved_pos, pos_component)

        health_component = entity.add_component(HealthComponent(100))
        self.assertIsInstance(health_component, HealthComponent)
        self.assertEqual(health_component.health, 100)

        retrieved_health = entity.get_component(HealthComponent)
        self.assertIs(retrieved_health, health_component)

    def test_add_duplicate_component_raises_error(self):
        """Test that adding a component of the same type twice raises an error."""
        entity = Entity()
        entity.add_component(PositionComponent())
        with self.assertRaises(ValueError):
            entity.add_component(PositionComponent())

    def test_get_nonexistent_component(self):
        """Test retrieving a component that has not been added."""
        entity = Entity()
        self.assertIsNone(entity.get_component(PositionComponent))

    def test_has_component(self):
        """Test checking for the existence of a component."""
        entity = Entity()
        self.assertFalse(entity.has_component(PositionComponent))
        entity.add_component(PositionComponent())
        self.assertTrue(entity.has_component(PositionComponent))
        self.assertFalse(entity.has_component(HealthComponent))

    def test_remove_component(self):
        """Test removing a component."""
        entity = Entity()
        pos_component = entity.add_component(PositionComponent())
        self.assertTrue(entity.has_component(PositionComponent))
        
        removed = entity.remove_component(PositionComponent)
        self.assertTrue(removed)
        self.assertFalse(entity.has_component(PositionComponent))
        self.assertIsNone(entity.get_component(PositionComponent))

        # Test removing a non-existent component
        removed_again = entity.remove_component(PositionComponent)
        self.assertFalse(removed_again)
        
        # Test removing a different non-existent component
        removed_health = entity.remove_component(HealthComponent)
        self.assertFalse(removed_health)

    def test_component_interaction(self):
        """Test interaction between components via the entity."""
        player = Entity()
        player.add_component(PositionComponent(x=0, y=0))
        player.add_component(InputComponent())

        input_comp = player.get_component(InputComponent)
        pos_comp = player.get_component(PositionComponent)

        self.assertIsNotNone(input_comp)
        self.assertIsNotNone(pos_comp)

        # Simulate input that moves the player
        input_comp.process_input(player, "move_right")
        self.assertEqual(pos_comp.x, 1)
        self.assertEqual(pos_comp.y, 0)
        self.assertEqual(input_comp.last_command, "move_right")

        input_comp.process_input(player, "move_left")
        input_comp.process_input(player, "move_left") # Move left twice
        self.assertEqual(pos_comp.x, -1) # 1 (from right) - 1 - 1 = -1
        self.assertEqual(pos_comp.y, 0)
        self.assertEqual(input_comp.last_command, "move_left")

    def test_entity_update_components(self):
        """Test that the entity can update all its components."""
        entity = Entity()
        input_comp = entity.add_component(InputComponent())
        input_comp.update = mock.Mock()

        # Add a component without an update method
        class NoUpdateComponent(Component):
            pass
        entity.add_component(NoUpdateComponent())
        
        # Add a component with an update method
        class CustomUpdateComponent(Component):
            def __init__(self):
                super().__init__()
                self.updated_with_entity = None
            def update(self, entity_arg):
                self.updated_with_entity = entity_arg
        custom_update_comp = entity.add_component(CustomUpdateComponent())

        entity.update_components()
        input_comp.update.assert_called_once_with(entity)
        self.assertIs(custom_update_comp.updated_with_entity, entity)

    def test_concrete_component_functionality(self):
        """Test specific functionalities of concrete components."""
        # PositionComponent
        pos = PositionComponent(5, 5)
        pos.move(1, -1)
        self.assertEqual(pos.x, 6)
        self.assertEqual(pos.y, 4)
        self.assertEqual(str(pos), "PositionComponent(x=6, y=4)")

        # HealthComponent
        health = HealthComponent(50)
        health.take_damage(20)
        self.assertEqual(health.health, 30)
        health.take_damage(40) # Health should go to 0, not negative
        self.assertEqual(health.health, 0)
        health.heal(10)
        self.assertEqual(health.health, 10)
        self.assertEqual(str(health), "HealthComponent(health=10)")

        # InputComponent (basic string representation)
        input_c = InputComponent()
        dummy_entity = Entity()
        input_c.process_input(dummy_entity, "jump")
        self.assertEqual(str(input_c), "InputComponent(last_command='jump')")

if __name__ == '__main__':
    unittest.main()
