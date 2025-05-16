\
"""
Tests for the Spatial Partition pattern.
"""
import unittest
from gpp.patterns.spatial_partition import SpatialObject, GridPartition

class TestSpatialPartition(unittest.TestCase):

    def test_grid_initialization(self):
        grid = GridPartition(cell_size=10, width=100, height=100)
        self.assertEqual(grid.grid_width, 10)
        self.assertEqual(grid.grid_height, 10)
        self.assertEqual(len(grid.grid), 10) # 10 rows
        self.assertEqual(len(grid.grid[0]), 10) # 10 columns in first row

        with self.assertRaisesRegex(ValueError, "Cell size must be positive."):
            GridPartition(cell_size=0, width=100, height=100)
        with self.assertRaisesRegex(ValueError, "Cell size must be positive."):
            GridPartition(cell_size=-5, width=100, height=100)
        with self.assertRaisesRegex(ValueError, "Grid width and height must be positive."):
            GridPartition(cell_size=10, width=0, height=100)
        with self.assertRaisesRegex(ValueError, "Grid width and height must be positive."):
            GridPartition(cell_size=10, width=100, height=0)

    def test_add_and_remove_object(self):
        grid = GridPartition(cell_size=10, width=100, height=100)
        obj1 = SpatialObject(obj_id="obj1", x=5, y=5)
        
        grid.add_object(obj1)
        cell_x, cell_y = grid._get_cell_coords(obj1.position)
        self.assertIn(obj1, grid.grid[cell_y][cell_x])
        self.assertEqual(grid.object_to_cell[obj1], (cell_x, cell_y))
        self.assertEqual(grid.get_object_cell(obj1), (0,0))

        # Test adding the same object again (should not duplicate or error)
        grid.add_object(obj1)
        self.assertEqual(len(grid.grid[cell_y][cell_x]), 1)

        grid.remove_object(obj1)
        self.assertNotIn(obj1, grid.grid[cell_y][cell_x])
        self.assertNotIn(obj1, grid.object_to_cell)

        # Test removing an object not in the grid
        obj_not_added = SpatialObject(obj_id="ghost", x=1, y=1)
        try:
            grid.remove_object(obj_not_added) # Should not raise error
        except Exception as e:
            self.fail(f"Removing a non-existent object raised an exception: {e}")

    def test_update_object_position(self):
        grid = GridPartition(cell_size=10, width=100, height=100)
        obj1 = SpatialObject(obj_id="obj1", x=5, y=5) # Cell (0,0)
        grid.add_object(obj1)

        # Update within the same cell
        grid.update_object_position(obj1, new_x=7, new_y=7)
        self.assertEqual(obj1.position, (7, 7))
        self.assertEqual(grid.get_object_cell(obj1), (0,0))
        self.assertIn(obj1, grid.grid[0][0])

        # Update to a different cell
        grid.update_object_position(obj1, new_x=15, new_y=15) # Cell (1,1)
        self.assertEqual(obj1.position, (15, 15))
        self.assertEqual(grid.get_object_cell(obj1), (1,1))
        self.assertNotIn(obj1, grid.grid[0][0])
        self.assertIn(obj1, grid.grid[1][1])

        # Update to edge of grid
        grid.update_object_position(obj1, new_x=95, new_y=95) # Cell (9,9)
        self.assertEqual(obj1.position, (95, 95))
        self.assertEqual(grid.get_object_cell(obj1), (9,9))
        self.assertIn(obj1, grid.grid[9][9])

        # Update to position outside grid (should clamp to edge cell)
        grid.update_object_position(obj1, new_x=105, new_y=105) # Clamps to (9,9)
        self.assertEqual(obj1.position, (105, 105))
        self.assertEqual(grid.get_object_cell(obj1), (9,9))
        self.assertIn(obj1, grid.grid[9][9])

        grid.update_object_position(obj1, new_x=-5, new_y=-5) # Clamps to (0,0)
        self.assertEqual(obj1.position, (-5, -5))
        self.assertEqual(grid.get_object_cell(obj1), (0,0))
        self.assertIn(obj1, grid.grid[0][0])

    def test_query_nearby(self):
        grid = GridPartition(cell_size=10, width=100, height=100)
        obj1 = SpatialObject(obj_id="obj1", x=5, y=5)    # Cell (0,0)
        obj2 = SpatialObject(obj_id="obj2", x=15, y=5)   # Cell (1,0)
        obj3 = SpatialObject(obj_id="obj3", x=5, y=15)   # Cell (0,1)
        obj4 = SpatialObject(obj_id="obj4", x=25, y=25)  # Cell (2,2)
        obj5 = SpatialObject(obj_id="obj5", x=50, y=50)  # Cell (5,5)

        grid.add_object(obj1)
        grid.add_object(obj2)
        grid.add_object(obj3)
        grid.add_object(obj4)
        grid.add_object(obj5)

        # Query around obj1
        nearby_to_obj1 = grid.query_nearby(position=(5,5), radius=10)
        self.assertIn(obj1, nearby_to_obj1)
        self.assertIn(obj2, nearby_to_obj1) # (15,5) is 10 units from (5,5)
        self.assertIn(obj3, nearby_to_obj1) # (5,15) is 10 units from (5,5)
        self.assertNotIn(obj4, nearby_to_obj1)
        self.assertNotIn(obj5, nearby_to_obj1)
        self.assertEqual(len(nearby_to_obj1), 3)

        # Query with radius 0
        nearby_at_obj1_pos = grid.query_nearby(position=(5,5), radius=0)
        self.assertIn(obj1, nearby_at_obj1_pos)
        self.assertEqual(len(nearby_at_obj1_pos), 1)

        # Query in an empty area
        empty_query = grid.query_nearby(position=(70,70), radius=5)
        self.assertEqual(len(empty_query), 0)

        # Query that covers multiple cells including one with obj4
        nearby_to_obj4_area = grid.query_nearby(position=(20,20), radius=10)
        self.assertNotIn(obj2, nearby_to_obj4_area)
        self.assertNotIn(obj3, nearby_to_obj4_area)
        self.assertIn(obj4, nearby_to_obj4_area) # (25,25) from (20,20). dx=5, dy=5. d^2 = 25+25 = 50. In.
        
        # Re-checking logic for nearby_to_obj4_area
        # Query center (20,20), radius 10
        # obj1 (5,5): dx=15, dy=15. d^2=225+225=450. Out.
        # obj2 (15,5): dx=5, dy=15. d^2=25+225=250. Out.
        # obj3 (5,15): dx=15, dy=5. d^2=225+25=250. Out.
        # obj4 (25,25): dx=5, dy=5. d^2=25+25=50. In.
        # obj5 (50,50): dx=30, dy=30. d^2=900+900=1800. Out.
        
        # Expected: only obj4
        self.assertNotIn(obj1, nearby_to_obj4_area)
        self.assertNotIn(obj2, nearby_to_obj4_area)
        self.assertNotIn(obj3, nearby_to_obj4_area)
        self.assertIn(obj4, nearby_to_obj4_area)
        self.assertEqual(len(nearby_to_obj4_area), 1)

        # Query that should grab obj5
        nearby_to_obj5 = grid.query_nearby(position=(48, 48), radius=5)
        self.assertIn(obj5, nearby_to_obj5)
        self.assertEqual(len(nearby_to_obj5), 1)

        # Query with negative radius
        with self.assertRaisesRegex(ValueError, "Radius must be non-negative."):
            grid.query_nearby(position=(0,0), radius=-1)

    def test_get_all_objects_in_cell(self):
        grid = GridPartition(cell_size=10, width=30, height=30)
        obj1 = SpatialObject(obj_id="obj1", x=5, y=5)    # Cell (0,0)
        obj2 = SpatialObject(obj_id="obj2", x=7, y=7)    # Cell (0,0)
        obj3 = SpatialObject(obj_id="obj3", x=15, y=15)  # Cell (1,1)
        grid.add_object(obj1)
        grid.add_object(obj2)
        grid.add_object(obj3)

        cell_0_0_objects = grid.get_all_objects_in_cell(0,0)
        self.assertIn(obj1, cell_0_0_objects)
        self.assertIn(obj2, cell_0_0_objects)
        self.assertEqual(len(cell_0_0_objects), 2)

        cell_1_1_objects = grid.get_all_objects_in_cell(1,1)
        self.assertIn(obj3, cell_1_1_objects)
        self.assertEqual(len(cell_1_1_objects), 1)

        empty_cell_objects = grid.get_all_objects_in_cell(2,2)
        self.assertEqual(len(empty_cell_objects), 0)

        # Test out of bounds cell access
        self.assertEqual(len(grid.get_all_objects_in_cell(-1,0)), 0)
        self.assertEqual(len(grid.get_all_objects_in_cell(0,-1)), 0)
        self.assertEqual(len(grid.get_all_objects_in_cell(grid.grid_width, 0)), 0)
        self.assertEqual(len(grid.get_all_objects_in_cell(0, grid.grid_height)), 0)

    def test_object_representation(self):
        obj = SpatialObject(obj_id=123, x=10.5, y=20.3)
        self.assertEqual(repr(obj), "SpatialObject(id=123, pos=(10.5, 20.3))")

    def test_grid_representation(self):
        grid = GridPartition(cell_size=5, width=50, height=25)
        self.assertEqual(repr(grid), "GridPartition(cell_size=5, grid_dims=(10x5))")

if __name__ == '__main__':
    unittest.main()
