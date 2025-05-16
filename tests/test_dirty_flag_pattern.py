\
import unittest
from gpp.patterns.dirty_flag import GameObject

class TestDirtyFlagPattern(unittest.TestCase):

    def test_initial_state_is_dirty_and_computes_on_first_get(self):
        obj = GameObject(10, 20, "TestObj")
        self.assertTrue(obj.is_dirty(), "Object should be dirty initially.")
        
        # First call to get_representation should compute
        representation = obj.get_representation()
        self.assertEqual(representation, "Object 'TestObj' at (10, 20)")
        self.assertFalse(obj.is_dirty(), "Object should not be dirty after getting representation.")

    def test_no_recomputation_if_not_dirty(self):
        obj = GameObject(1, 2, "Obj1")
        
        # First call computes
        first_rep = obj.get_representation()
        self.assertFalse(obj.is_dirty())
        
        # Second call should return cached value without recomputing
        # We can't directly check if computation happened without more sophisticated mocking
        # or by inspecting internal state/logs if the class provided them.
        # For this test, we rely on the dirty flag state.
        second_rep = obj.get_representation()
        self.assertEqual(first_rep, second_rep)
        self.assertFalse(obj.is_dirty(), "Object should remain not dirty.")

    def test_setting_property_marks_dirty_and_recomputes(self):
        obj = GameObject(5, 5, "Obj2")
        obj.get_representation() # Initial computation, clears dirty flag
        self.assertFalse(obj.is_dirty())

        obj.x = 15 # Change property, should mark as dirty
        self.assertTrue(obj.is_dirty(), "Object should be dirty after changing x.")

        new_representation = obj.get_representation() # Should recompute
        self.assertEqual(new_representation, "Object 'Obj2' at (15, 5)")
        self.assertFalse(obj.is_dirty(), "Object should not be dirty after recomputing.")

        obj.y = 25 # Change another property
        self.assertTrue(obj.is_dirty(), "Object should be dirty after changing y.")
        
        another_rep = obj.get_representation()
        self.assertEqual(another_rep, "Object 'Obj2' at (15, 25)")
        self.assertFalse(obj.is_dirty())

        obj.name = "NewName" # Change name
        self.assertTrue(obj.is_dirty(), "Object should be dirty after changing name.")
        
        name_change_rep = obj.get_representation()
        self.assertEqual(name_change_rep, "Object 'NewName' at (15, 25)")
        self.assertFalse(obj.is_dirty())

    def test_setting_property_to_same_value_does_not_mark_dirty(self):
        obj = GameObject(100, 200, "StableObj")
        obj.get_representation() # Initial computation
        self.assertFalse(obj.is_dirty())

        obj.x = 100 # Set x to its current value
        self.assertFalse(obj.is_dirty(), "Object should not be dirty if x is set to the same value.")
        
        obj.y = 200 # Set y to its current value
        self.assertFalse(obj.is_dirty(), "Object should not be dirty if y is set to the same value.")

        obj.name = "StableObj" # Set name to its current value
        self.assertFalse(obj.is_dirty(), "Object should not be dirty if name is set to the same value.")

        # Ensure representation is still the original one without recomputation
        representation = obj.get_representation()
        self.assertEqual(representation, "Object 'StableObj' at (100, 200)")
        self.assertFalse(obj.is_dirty())

if __name__ == '__main__':
    unittest.main()
