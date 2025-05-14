"""
Unit tests for the Type Object pattern.
"""
import unittest
from gpp.patterns.type_object import TypeObject, TypedObject

class TestTypeObjectPattern(unittest.TestCase):
    """Tests the Type Object pattern implementation."""

    def setUp(self):
        """Set up for test methods."""
        self.monster_type = TypeObject(name="Monster", shared_attribute="Roars")
        self.hero_type = TypeObject(name="Hero", shared_attribute="Speaks")

    def test_type_object_creation(self):
        """Test the creation of TypeObject instances."""
        self.assertEqual(self.monster_type.name, "Monster")
        self.assertEqual(self.monster_type.shared_attribute, "Roars")
        self.assertEqual(self.hero_type.name, "Hero")
        self.assertEqual(self.hero_type.shared_attribute, "Speaks")

    def test_type_object_shared_behavior(self):
        """Test the shared behavior of TypeObject."""
        self.assertEqual(self.monster_type.get_shared_behavior(), "Shared behavior from Monster type: Roars")
        self.assertEqual(self.hero_type.get_shared_behavior(), "Shared behavior from Hero type: Speaks")

    def test_typed_object_creation_and_type_reference(self):
        """Test creation of TypedObject and its reference to TypeObject."""
        goblin = TypedObject(type_obj=self.monster_type, instance_attribute="Green skin")
        knight = TypedObject(type_obj=self.hero_type, instance_attribute="Shining armor")

        self.assertIs(goblin.type, self.monster_type)
        self.assertEqual(goblin.instance_attribute, "Green skin")
        self.assertIs(knight.type, self.hero_type)
        self.assertEqual(knight.instance_attribute, "Shining armor")

    def test_typed_object_instance_data(self):
        """Test accessing instance-specific data."""
        goblin = TypedObject(type_obj=self.monster_type, instance_attribute="Slimy")
        self.assertEqual(goblin.get_instance_data(), "Slimy")

    def test_typed_object_delegates_shared_action(self):
        """Test that TypedObject delegates shared actions to its TypeObject."""
        orc = TypedObject(type_obj=self.monster_type, instance_attribute="Big tusks")
        wizard = TypedObject(type_obj=self.hero_type, instance_attribute="Long beard")

        self.assertEqual(orc.perform_shared_action(), "Shared behavior from Monster type: Roars")
        self.assertEqual(wizard.perform_shared_action(), "Shared behavior from Hero type: Speaks")

    def test_objects_of_same_type_share_type_object(self):
        """Test that multiple TypedObjects can share the same TypeObject."""
        goblin1 = TypedObject(type_obj=self.monster_type, instance_attribute="Small club")
        goblin2 = TypedObject(type_obj=self.monster_type, instance_attribute="Rusty dagger")

        self.assertIs(goblin1.type, self.monster_type)
        self.assertIs(goblin2.type, self.monster_type)
        self.assertIs(goblin1.type, goblin2.type)

        # Modifying the shared attribute on the TypeObject affects all instances
        self.monster_type.shared_attribute = "Growls loudly"
        self.assertEqual(goblin1.perform_shared_action(), "Shared behavior from Monster type: Growls loudly")
        self.assertEqual(goblin2.perform_shared_action(), "Shared behavior from Monster type: Growls loudly")

    def test_objects_of_different_types_have_different_type_objects(self):
        """Test that TypedObjects of different conceptual types have different TypeObjects."""
        dragon = TypedObject(type_obj=self.monster_type, instance_attribute="Breathes fire")
        paladin = TypedObject(type_obj=self.hero_type, instance_attribute="Holy hammer")

        self.assertIsNot(dragon.type, paladin.type)
        self.assertEqual(dragon.perform_shared_action(), "Shared behavior from Monster type: Roars")
        self.assertEqual(paladin.perform_shared_action(), "Shared behavior from Hero type: Speaks")

    def test_str_representation(self):
        """Test the string representation of TypedObject."""
        slime = TypedObject(type_obj=self.monster_type, instance_attribute="Gelatinous")
        expected_str = "Instance of Monster (Instance: Gelatinous, Shared: Roars)"
        self.assertEqual(str(slime), expected_str)

        archer = TypedObject(type_obj=self.hero_type, instance_attribute="Keen eyes")
        expected_str_hero = "Instance of Hero (Instance: Keen eyes, Shared: Speaks)"
        self.assertEqual(str(archer), expected_str_hero)

if __name__ == '__main__':
    unittest.main()
