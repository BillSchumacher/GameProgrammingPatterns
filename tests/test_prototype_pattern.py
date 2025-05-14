import unittest
import copy
from gpp.patterns.prototype import Prototype


class TestConcretePrototype(Prototype):
    def __init__(self, field, mutable_field):
        self.field = field
        self.mutable_field = mutable_field
        self._constructor_args = (field, mutable_field)

    def clone(self):
        return self.__class__(*self._constructor_args)

    def __str__(self):
        return f"TestConcretePrototype(field={self.field!r}, mutable_field={self.mutable_field!r})"

class TestDeepConcretePrototype(Prototype):
    def __init__(self, field, mutable_field):
        self.field = field
        self.mutable_field = copy.deepcopy(mutable_field)
        self._constructor_args = (field, mutable_field)

    def clone(self):
        return self.__class__(*self._constructor_args)

    def __str__(self):
        return f"TestDeepConcretePrototype(field={self.field!r}, mutable_field={self.mutable_field!r})"

class TestPrototypePattern(unittest.TestCase):

    def test_constructor_clone_creates_new_object(self):
        original = TestConcretePrototype("value1", [1, 2])
        clone = original.clone()
        self.assertIsNot(original, clone, "Clone should be a new object.")
        # For TestConcretePrototype, constructor reuses the mutable_field reference from _constructor_args
        self.assertIs(original.mutable_field, clone.mutable_field, "Mutable field should be the same object as constructor reuses the passed reference.")
        self.assertEqual(original.mutable_field, clone.mutable_field, "Mutable field content should be the same initially.")

    def test_constructor_clone_copies_immutable_field(self):
        original = TestConcretePrototype("value1", [1, 2])
        clone = original.clone()
        self.assertEqual(original.field, clone.field, "Immutable field should be equal.")

    def test_constructor_clone_mutable_field_behavior(self):
        original_list = [1, 2]
        original = TestConcretePrototype("value1", original_list)
        clone = original.clone()
        self.assertIs(original.mutable_field, clone.mutable_field, "Mutable field should be the same object if constructor reuses the passed reference.")

        clone.mutable_field.append(3)
        self.assertEqual(original.mutable_field, [1, 2, 3],
                         "Change in clone's mutable field affects original if constructor shares the reference.")

    def test_deep_constructor_clone_creates_new_object(self):
        original = TestDeepConcretePrototype("value1", [1, 2, {"a": "A"}])
        clone = original.clone()
        self.assertIsNot(original, clone, "Clone should be a new object.")

    def test_deep_constructor_clone_copies_immutable_field(self):
        original = TestDeepConcretePrototype("value1", [1, 2, {"a": "A"}])
        clone = original.clone()
        self.assertEqual(original.field, clone.field, "Immutable field should be equal.")

    def test_deep_constructor_clone_creates_independent_mutable_field(self):
        original_mutable_data = [1, 2, {"a": "A"}]
        original = TestDeepConcretePrototype("value1", original_mutable_data)
        clone = original.clone()
        
        self.assertIsNot(original.mutable_field, clone.mutable_field, 
                         "Mutable field in clone should be a new object due to deepcopy in constructor.")
        self.assertEqual(original.mutable_field, clone.mutable_field, 
                         "Mutable fields should have the same content initially.")

        clone.mutable_field.append(3)
        clone.mutable_field[2]["a"] = "Z"
        self.assertEqual(original.mutable_field, [1, 2, {"a": "A"}], 
                         "Change in clone's mutable field should NOT affect original's.")
        self.assertEqual(clone.mutable_field, [1, 2, {"a": "Z"}, 3])

        original.mutable_field.append(4)
        original.mutable_field[2]["a"] = "B"
        self.assertEqual(clone.mutable_field, [1, 2, {"a": "Z"}, 3], 
                         "Change in original's mutable field should NOT affect clone's.")
        self.assertEqual(original.mutable_field, [1, 2, {"a": "B"}, 4])

if __name__ == '__main__':
    unittest.main()
