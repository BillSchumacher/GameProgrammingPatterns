import unittest
from gamepp.patterns.dirty_flag import GameObject


class TestDirtyFlagPattern(unittest.TestCase):
    def test_initial_state_is_dirty_and_computes_on_first_get(self):
        obj = GameObject(10, 20, "TestObj")
        self.assertTrue(
            obj.is_dirty(), "Object should be dirty initially for representation."
        )
        self.assertTrue(
            obj._is_world_transform_dirty,
            "Object should be dirty initially for world transform.",
        )

        # First call to get_representation should compute
        representation = obj.get_representation()
        expected_repr = "Object 'TestObj' at world (10.00, 20.00), local (10.00, 20.00)"
        self.assertEqual(representation, expected_repr)
        self.assertFalse(
            obj.is_dirty(),
            "Object representation should not be dirty after getting representation.",
        )
        self.assertFalse(
            obj._is_world_transform_dirty,
            "Object world transform should not be dirty after getting representation.",
        )

    def test_no_recomputation_if_not_dirty(self):
        obj = GameObject(1, 2, "Obj1")

        # First call computes
        first_rep = obj.get_representation()
        self.assertFalse(obj.is_dirty())
        self.assertFalse(obj._is_world_transform_dirty)

        # Second call should return cached value
        second_rep = obj.get_representation()
        self.assertEqual(first_rep, second_rep)
        self.assertFalse(
            obj.is_dirty(), "Object representation should remain not dirty."
        )
        self.assertFalse(
            obj._is_world_transform_dirty,
            "Object world transform should remain not dirty.",
        )

    def test_setting_local_property_marks_transform_and_representation_dirty(self):
        obj = GameObject(5, 5, "Obj2")
        obj.get_representation()  # Initial computation, clears dirty flags
        self.assertFalse(obj.is_dirty())
        self.assertFalse(obj._is_world_transform_dirty)

        obj.local_x = 15  # Change local property
        self.assertTrue(
            obj.is_dirty(), "Representation should be dirty after changing local_x."
        )
        self.assertTrue(
            obj._is_world_transform_dirty,
            "World transform should be dirty after changing local_x.",
        )

        new_representation = obj.get_representation()
        expected_repr = "Object 'Obj2' at world (15.00, 5.00), local (15.00, 5.00)"
        self.assertEqual(new_representation, expected_repr)
        self.assertFalse(
            obj.is_dirty(), "Representation should not be dirty after recomputing."
        )
        self.assertFalse(
            obj._is_world_transform_dirty,
            "World transform should not be dirty after recomputing.",
        )

        obj.local_y = 25
        self.assertTrue(obj.is_dirty())
        self.assertTrue(obj._is_world_transform_dirty)

        another_rep = obj.get_representation()
        expected_repr_y = "Object 'Obj2' at world (15.00, 25.00), local (15.00, 25.00)"
        self.assertEqual(another_rep, expected_repr_y)
        self.assertFalse(obj.is_dirty())
        self.assertFalse(obj._is_world_transform_dirty)

    def test_setting_name_marks_only_representation_dirty(self):
        obj = GameObject(10, 10, "NameObj")
        obj.get_representation()  # Initial computation
        self.assertFalse(obj.is_dirty())
        self.assertFalse(obj._is_world_transform_dirty)

        obj.name = "NewNameObj"
        self.assertTrue(
            obj.is_dirty(), "Representation should be dirty after changing name."
        )
        # World transform should NOT be dirty just because name changed
        self.assertFalse(
            obj._is_world_transform_dirty,
            "World transform should NOT be dirty after changing name.",
        )

        name_change_rep = obj.get_representation()
        expected_repr_name = (
            "Object 'NewNameObj' at world (10.00, 10.00), local (10.00, 10.00)"
        )
        self.assertEqual(name_change_rep, expected_repr_name)
        self.assertFalse(obj.is_dirty())
        self.assertFalse(obj._is_world_transform_dirty)

    def test_setting_property_to_same_value_does_not_mark_dirty(self):
        obj = GameObject(100, 200, "StableObj")
        obj.get_representation()  # Initial computation
        self.assertFalse(obj.is_dirty())
        self.assertFalse(obj._is_world_transform_dirty)

        obj.local_x = 100
        self.assertFalse(
            obj.is_dirty(),
            "Representation should not be dirty if local_x is set to the same value.",
        )
        self.assertFalse(
            obj._is_world_transform_dirty,
            "World transform should not be dirty if local_x is set to the same value.",
        )

        obj.local_y = 200
        self.assertFalse(obj.is_dirty())
        self.assertFalse(obj._is_world_transform_dirty)

        obj.name = "StableObj"
        self.assertFalse(obj.is_dirty())
        self.assertFalse(
            obj._is_world_transform_dirty
        )  # Name change doesn't affect transform

        representation = obj.get_representation()
        expected_repr = (
            "Object 'StableObj' at world (100.00, 200.00), local (100.00, 200.00)"
        )
        self.assertEqual(representation, expected_repr)
        self.assertFalse(obj.is_dirty())
        self.assertFalse(obj._is_world_transform_dirty)

    def test_parent_child_transform_dirty_propagation(self):
        parent_obj = GameObject(10, 10, "Parent")
        child_obj = GameObject(5, 5, "Child", parent=parent_obj)

        # Initial get_representation to clear flags for both
        parent_obj.get_representation()  # Clears parent's flags
        child_obj.get_representation()  # Clears child's flags (and re-calculates parent transform if needed)

        self.assertFalse(
            parent_obj.is_dirty(),
            "Parent representation should be clean after initial get.",
        )
        self.assertFalse(
            parent_obj._is_world_transform_dirty,
            "Parent transform should be clean after initial get.",
        )
        self.assertFalse(
            child_obj.is_dirty(),
            "Child representation should be clean after initial get.",
        )
        self.assertFalse(
            child_obj._is_world_transform_dirty,
            "Child transform should be clean after initial get.",
        )

        expected_child_rep_initial = (
            "Object 'Child' at world (15.00, 15.00), local (5.00, 5.00)"
        )
        # Re-fetch child representation for assertion as parent's get_representation might have re-cached it if it was first
        self.assertEqual(child_obj.get_representation(), expected_child_rep_initial)

        # Change parent's local_x, should dirty both parent and child transforms and representations
        parent_obj.local_x = 20
        self.assertTrue(
            parent_obj.is_dirty(),
            "Parent representation should be dirty after local_x change.",
        )
        self.assertTrue(
            parent_obj._is_world_transform_dirty,
            "Parent transform should be dirty after local_x change.",
        )
        self.assertTrue(
            child_obj.is_dirty(),
            "Child representation should be dirty due to parent change.",
        )
        self.assertTrue(
            child_obj._is_world_transform_dirty,
            "Child transform should be dirty due to parent change.",
        )

        # Get child's representation. This will recompute child's world transform,
        # which in turn recomputes parent's world transform.
        new_child_rep = child_obj.get_representation()
        expected_child_rep_after_parent_move = (
            "Object 'Child' at world (25.00, 15.00), local (5.00, 5.00)"
        )
        self.assertEqual(new_child_rep, expected_child_rep_after_parent_move)

        # After child's get_representation:
        # Child's flags are cleared.
        self.assertFalse(
            child_obj.is_dirty(),
            "Child representation should be clean after its get_representation.",
        )
        self.assertFalse(
            child_obj._is_world_transform_dirty,
            "Child transform should be clean after its get_representation.",
        )

        # Parent's world transform was recomputed as a dependency, so it's clean.
        self.assertFalse(
            parent_obj._is_world_transform_dirty,
            "Parent's world transform should be clean after child's get_representation caused its update.",
        )
        # However, parent's *representation* (_is_dirty) is still True because parent.get_representation() itself was not called for the parent object directly after the change.
        self.assertTrue(
            parent_obj.is_dirty(),
            "Parent's representation flag should still be true as only its transform was implicitly updated.",
        )

        # Now, explicitly get parent's representation. This should use the updated (clean) transform
        # and clear the parent's _is_dirty flag for representation.
        parent_rep_after_child_update = parent_obj.get_representation()
        expected_parent_rep_after_change = (
            "Object 'Parent' at world (20.00, 10.00), local (20.00, 10.00)"
        )
        self.assertEqual(
            parent_rep_after_child_update, expected_parent_rep_after_change
        )
        self.assertFalse(
            parent_obj.is_dirty(),
            "Parent's representation should be clean after its own get_representation call.",
        )
        self.assertFalse(
            parent_obj._is_world_transform_dirty,
            "Parent's transform should remain clean.",
        )

    def test_reparenting_marks_child_dirty(self):
        obj1 = GameObject(1, 1, "Obj1")
        obj2 = GameObject(2, 2, "Obj2")
        child = GameObject(10, 10, "Child", parent=obj1)

        child.get_representation()  # Initial calculation
        self.assertFalse(child.is_dirty())
        self.assertFalse(child._is_world_transform_dirty)
        # Initial world: Obj1(1,1) + Child(10,10) = (11,11)

        child.parent = obj2  # Reparent
        self.assertTrue(
            child.is_dirty(), "Child representation should be dirty after reparenting."
        )
        self.assertTrue(
            child._is_world_transform_dirty,
            "Child transform should be dirty after reparenting.",
        )

        new_rep = child.get_representation()
        # New world: Obj2(2,2) + Child(10,10) = (12,12)
        expected_rep = "Object 'Child' at world (12.00, 12.00), local (10.00, 10.00)"
        self.assertEqual(new_rep, expected_rep)
        self.assertFalse(child.is_dirty())
        self.assertFalse(child._is_world_transform_dirty)

    def test_changing_child_local_transform_does_not_dirty_parent(self):
        parent = GameObject(1, 1, "Parent")
        child = GameObject(5, 5, "Child", parent=parent)

        parent.get_representation()
        child.get_representation()
        self.assertFalse(parent.is_dirty())
        self.assertFalse(parent._is_world_transform_dirty)
        self.assertFalse(child.is_dirty())
        self.assertFalse(child._is_world_transform_dirty)

        child.local_x = 15
        self.assertTrue(child.is_dirty())
        self.assertTrue(child._is_world_transform_dirty)
        self.assertFalse(
            parent.is_dirty(),
            "Parent representation should NOT be dirty when child's local transform changes.",
        )
        self.assertFalse(
            parent._is_world_transform_dirty,
            "Parent transform should NOT be dirty when child's local transform changes.",
        )

        child_rep = child.get_representation()
        expected_child_rep = "Object 'Child' at world (16.00, 6.00), local (15.00, 5.00)"  # Parent(1,1) + Child(15,5)
        self.assertEqual(child_rep, expected_child_rep)

        # Parent should still not be dirty
        self.assertFalse(parent.is_dirty())
        self.assertFalse(parent._is_world_transform_dirty)
        parent_rep = parent.get_representation()  # Should not recompute
        expected_parent_rep = (
            "Object 'Parent' at world (1.00, 1.00), local (1.00, 1.00)"
        )
        self.assertEqual(parent_rep, expected_parent_rep)


if __name__ == "__main__":
    unittest.main()
