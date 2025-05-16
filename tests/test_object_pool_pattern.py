"""
Tests for the Object Pool pattern.
"""
import unittest
from typing import Optional

from gpp.patterns.object_pool import PooledObject, ObjectPool


class MyUniqueResource(PooledObject):
    _next_id = 0

    def __init__(self):
        super().__init__()
        self.resource_id = MyUniqueResource._next_id
        MyUniqueResource._next_id += 1
        self.data: Optional[str] = None
        # To avoid printing during tests, comment out or remove print statements
        # print(f"MyUniqueResource {self.resource_id} created.")

    def set_data(self, data: str) -> None:
        self.data = data

    def get_data(self) -> Optional[str]:
        return self.data

    def reset(self) -> None:
        super().reset()
        # print(f"MyUniqueResource {self.resource_id} reset. Data cleared.")
        self.data = None
        # Reset _next_id for consistent test runs if objects are created outside pool
        # or if the test re-initializes pools multiple times in a way that this matters.
        # For this specific test structure, it might not be strictly necessary
        # if each test method manages its own pool and resource creation lifecycle.

class TestObjectPool(unittest.TestCase):
    def setUp(self) -> None:
        """Reset class variables for ID generation before each test."""
        MyUniqueResource._next_id = 0

    def test_object_pool_workflow(self):
        # print("\nInitializing ObjectPool for MyUniqueResource...")
        unique_resource_pool = ObjectPool(MyUniqueResource, pool_size=2)

        # print(f"Initial pool info: {unique_resource_pool.get_pool_info()}")
        self.assertEqual(unique_resource_pool.get_pool_info(), {
            "total_objects": 2, "used_objects": 0, "available_objects": 2
        })

        # Acquire objects
        # print("\nAcquiring objects...")
        r1 = unique_resource_pool.acquire_object()
        self.assertIsNotNone(r1)
        if r1: # Check to satisfy type checker, though assertIsNotNone covers it
            self.assertTrue(r1.is_in_use())
            self.assertEqual(r1.resource_id, 0) # Assuming IDs start from 0
            r1.set_data("Data for R1")
            # print(f"Acquired R1 (ID: {r1.resource_id}), In use: {r1.is_in_use()}")

        r2 = unique_resource_pool.acquire_object()
        self.assertIsNotNone(r2)
        if r2:
            self.assertTrue(r2.is_in_use())
            self.assertEqual(r2.resource_id, 1)
            r2.set_data("Data for R2")
            # print(f"Acquired R2 (ID: {r2.resource_id}), In use: {r2.is_in_use()}")

        # print(f"Pool info after acquiring two: {unique_resource_pool.get_pool_info()}")
        self.assertEqual(unique_resource_pool.get_pool_info(), {
            "total_objects": 2, "used_objects": 2, "available_objects": 0
        })

        r3 = unique_resource_pool.acquire_object()
        self.assertIsNone(r3) # Pool exhausted
        # print("Could not acquire R3 (pool exhausted as expected).")

        # Release an object
        # print("\nReleasing R1...")
        if r1:
            unique_resource_pool.release_object(r1)
            self.assertFalse(r1.is_in_use())
            self.assertIsNone(r1.get_data()) # Data should be cleared by reset
            # print(f"R1 released. In use: {r1.is_in_use()}, Data: {r1.get_data()}")
        
        # print(f"Pool info after releasing R1: {unique_resource_pool.get_pool_info()}")
        self.assertEqual(unique_resource_pool.get_pool_info(), {
            "total_objects": 2, "used_objects": 1, "available_objects": 1
        })

        # Acquire again (should get R1, which is now reset)
        # print("\nAcquiring again...")
        r4 = unique_resource_pool.acquire_object()
        self.assertIsNotNone(r4)
        if r4:
            self.assertTrue(r4.is_in_use())
            self.assertEqual(r4.resource_id, 0) # Should be the first object, reset
            self.assertIsNone(r4.get_data()) # Should be reset
            r4.set_data("New data for R4 (reused R1)")
            # print(f"Acquired R4 (ID: {r4.resource_id}), In use: {r4.is_in_use()}")
            # print(f"R4's data (should be None as it was reset): {r4.get_data()}")

        # print(f"Pool info at the end: {unique_resource_pool.get_pool_info()}")
        self.assertEqual(unique_resource_pool.get_pool_info(), {
            "total_objects": 2, "used_objects": 2, "available_objects": 0
        })

    def test_error_cases(self):
        # print("\nTesting error cases...")
        unique_resource_pool = ObjectPool(MyUniqueResource, pool_size=1)

        class NotPooled:
            pass
        
        not_pooled_obj = NotPooled()
        with self.assertRaisesRegex(ValueError, "Object being released is not a PooledObject instance."):
            # This will fail type check if strict static analysis is used before runtime
            unique_resource_pool.release_object(not_pooled_obj) # type: ignore

        another_resource = MyUniqueResource() # Created outside the pool
        with self.assertRaisesRegex(ValueError, "Object being released does not belong to this pool."):
            unique_resource_pool.release_object(another_resource)

        # Test releasing an already released object (current pool allows, calls reset again)
        obj1 = unique_resource_pool.acquire_object()
        self.assertIsNotNone(obj1)
        if obj1:
            unique_resource_pool.release_object(obj1)
            self.assertFalse(obj1.is_in_use())
            # Attempt to release again - should not error with current implementation
            # but simply call reset again.
            try:
                unique_resource_pool.release_object(obj1)
            except ValueError:
                self.fail("Releasing an already released object raised ValueError unexpectedly.")
            self.assertFalse(obj1.is_in_use()) # Still not in use

    def test_pool_initialization_errors(self):
        with self.assertRaisesRegex(ValueError, "Pool size must be a positive integer."):
            ObjectPool(MyUniqueResource, pool_size=0)
        with self.assertRaisesRegex(ValueError, "Pool size must be a positive integer."):
            ObjectPool(MyUniqueResource, pool_size=-1)
        
        class NonPooledObject:
            pass

        with self.assertRaisesRegex(TypeError, "Class NonPooledObject must inherit from PooledObject."):
            ObjectPool(NonPooledObject, pool_size=1) # type: ignore

if __name__ == '__main__':
    unittest.main()
