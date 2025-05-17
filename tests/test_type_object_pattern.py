"""
Unit tests for the Type Object pattern.
"""

import unittest
from gamepp.patterns.type_object import TypeObject, TypedObject


class TestTypeObjectPattern(unittest.TestCase):
    """Tests the Type Object pattern implementation."""

    def setUp(self):
        """Set up for test methods."""
        # Updated to use health and attack attributes
        self.base_monster_type = TypeObject(
            name="BaseMonster", health=50, attack="Base Roar"
        )
        self.troll_type = TypeObject(
            name="Troll",
            health=100,
            attack="Troll Smash",
            parent=self.base_monster_type,
        )
        self.goblin_type = TypeObject(
            name="Goblin", health=0, attack="Goblin Stab", parent=self.base_monster_type
        )  # Inherits health
        self.hero_type = TypeObject(name="Hero", health=75, attack="Heroic Strike")

    def test_type_object_creation(self):
        """Test the creation of TypeObject instances."""
        self.assertEqual(self.troll_type.name, "Troll")
        self.assertEqual(self.troll_type.health, 100)  # Overridden
        self.assertEqual(self.troll_type.attack, "Troll Smash")  # Overridden

        self.assertEqual(self.goblin_type.name, "Goblin")
        self.assertEqual(self.goblin_type.health, 50)  # Inherited from BaseMonster
        self.assertEqual(self.goblin_type.attack, "Goblin Stab")  # Overridden

        self.assertEqual(self.hero_type.name, "Hero")
        self.assertEqual(self.hero_type.health, 75)
        self.assertEqual(self.hero_type.attack, "Heroic Strike")

    def test_type_object_shared_behavior(self):
        """Test the shared behavior of TypeObject."""
        self.assertEqual(
            self.troll_type.get_shared_behavior(),
            "Type 'Troll': Health = 100, Attack = 'Troll Smash'",
        )
        self.assertEqual(
            self.goblin_type.get_shared_behavior(),
            "Type 'Goblin': Health = 50, Attack = 'Goblin Stab'",
        )
        self.assertEqual(
            self.hero_type.get_shared_behavior(),
            "Type 'Hero': Health = 75, Attack = 'Heroic Strike'",
        )

    def test_typed_object_creation_and_type_reference(self):
        """Test creation of TypedObject and its reference to TypeObject."""
        troll_warrior = TypedObject(
            type_obj=self.troll_type, instance_attribute="Wears heavy armor"
        )
        hero_archer = TypedObject(type_obj=self.hero_type, instance_attribute="Longbow")

        self.assertIs(troll_warrior.type, self.troll_type)
        self.assertEqual(troll_warrior.instance_attribute, "Wears heavy armor")
        self.assertIs(hero_archer.type, self.hero_type)
        self.assertEqual(hero_archer.instance_attribute, "Longbow")

    def test_typed_object_instance_data(self):
        """Test accessing instance-specific data."""
        goblin_scout = TypedObject(
            type_obj=self.goblin_type, instance_attribute="Fast runner"
        )
        self.assertEqual(goblin_scout.get_instance_data(), "Fast runner")

    def test_typed_object_delegates_shared_action(self):
        """Test that TypedObject delegates shared actions to its TypeObject."""
        orc_berserker = TypedObject(
            type_obj=self.troll_type, instance_attribute="Dual axes"
        )  # Using troll_type for variety
        knight_paladin = TypedObject(
            type_obj=self.hero_type, instance_attribute="Holy shield"
        )

        self.assertEqual(
            orc_berserker.perform_shared_action(),
            "Type 'Troll': Health = 100, Attack = 'Troll Smash'",
        )
        self.assertEqual(
            knight_paladin.perform_shared_action(),
            "Type 'Hero': Health = 75, Attack = 'Heroic Strike'",
        )

    def test_objects_of_same_type_share_type_object(self):
        """Test that multiple TypedObjects can share the same TypeObject."""
        goblin1 = TypedObject(
            type_obj=self.goblin_type, instance_attribute="Small club"
        )
        goblin2 = TypedObject(
            type_obj=self.goblin_type, instance_attribute="Rusty dagger"
        )

        self.assertIs(goblin1.type, self.goblin_type)
        self.assertIs(goblin2.type, self.goblin_type)
        self.assertIs(goblin1.type, goblin2.type)

        # With copy-down, modifying the original TypeObject's _health or _attack
        # after child TypedObjects are created won't affect them directly,
        # as the values were copied at instantiation.
        # This part of the test is different from when shared_attribute was mutable directly on the TypeObject.
        # We are testing that they share the same type, and thus the same initial shared behavior.
        self.assertEqual(
            goblin1.perform_shared_action(),
            "Type 'Goblin': Health = 50, Attack = 'Goblin Stab'",
        )
        self.assertEqual(
            goblin2.perform_shared_action(),
            "Type 'Goblin': Health = 50, Attack = 'Goblin Stab'",
        )

    def test_objects_of_different_types_have_different_type_objects(self):
        """Test that TypedObjects of different conceptual types have different TypeObjects."""
        dragon = TypedObject(
            type_obj=self.troll_type, instance_attribute="Breathes fire"
        )  # Using troll_type
        paladin = TypedObject(type_obj=self.hero_type, instance_attribute="Holy hammer")

        self.assertIsNot(dragon.type, paladin.type)
        self.assertEqual(
            dragon.perform_shared_action(),
            "Type 'Troll': Health = 100, Attack = 'Troll Smash'",
        )
        self.assertEqual(
            paladin.perform_shared_action(),
            "Type 'Hero': Health = 75, Attack = 'Heroic Strike'",
        )

    def test_str_representation(self):
        """Test the string representation of TypedObject."""
        slime = TypedObject(
            type_obj=self.goblin_type, instance_attribute="Gelatinous"
        )  # Using goblin_type
        expected_str = "Instance of 'Goblin' (Instance Data: 'Gelatinous', Type Health: 50, Type Attack: 'Goblin Stab')"
        self.assertEqual(str(slime), expected_str)

        archer = TypedObject(type_obj=self.hero_type, instance_attribute="Keen eyes")
        expected_str_hero = "Instance of 'Hero' (Instance Data: 'Keen eyes', Type Health: 75, Type Attack: 'Heroic Strike')"
        self.assertEqual(str(archer), expected_str_hero)


if __name__ == "__main__":
    unittest.main()
