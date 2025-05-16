"""
Spatial Partition Pattern Implementation
"""
from typing import List, Tuple, Set, Generic, TypeVar

# Define a type variable for objects that can be stored in the spatial partition
T = TypeVar('T')

class SpatialObject(Generic[T]):
    """
    Base class for objects that can be stored in a spatial partition.
    Each object must have a position.
    """
    def __init__(self, obj_id: T, x: float, y: float):
        self.obj_id = obj_id
        self.position: Tuple[float, float] = (x, y)

    def __repr__(self) -> str:
        return f"SpatialObject(id={self.obj_id}, pos={self.position})"

class GridPartition:
    """
    A simple grid-based spatial partition.
    Organizes objects into cells based on their positions.
    """
    def __init__(self, cell_size: float, width: float, height: float):
        if cell_size <= 0:
            raise ValueError("Cell size must be positive.")
        if width <= 0 or height <= 0:
            raise ValueError("Grid width and height must be positive.")

        self.cell_size = cell_size
        self.grid_width = int(width / cell_size)
        self.grid_height = int(height / cell_size)
        
        # Initialize grid: a list of lists, where each inner list is a row of cells,
        # and each cell is a set of objects.
        self.grid: List[List[Set[SpatialObject]]] = [
            [set() for _ in range(self.grid_width)] for _ in range(self.grid_height)
        ]
        self.object_to_cell: dict[SpatialObject, Tuple[int, int]] = {}

    def _get_cell_coords(self, position: Tuple[float, float]) -> Tuple[int, int]:
        """Converts world position to grid cell coordinates."""
        x, y = position
        cell_x = int(x / self.cell_size)
        cell_y = int(y / self.cell_size)
        
        # Clamp coordinates to be within grid boundaries
        cell_x = max(0, min(cell_x, self.grid_width - 1))
        cell_y = max(0, min(cell_y, self.grid_height - 1))
        return cell_x, cell_y

    def add_object(self, obj: SpatialObject) -> None:
        """Adds an object to the spatial partition."""
        if obj in self.object_to_cell:
            # Object already in grid, perhaps update its position if needed
            # For simplicity, let's assume add is for new objects or re-adding after removal
            return 

        cell_x, cell_y = self._get_cell_coords(obj.position)
        self.grid[cell_y][cell_x].add(obj)
        self.object_to_cell[obj] = (cell_x, cell_y)

    def remove_object(self, obj: SpatialObject) -> None:
        """Removes an object from the spatial partition."""
        if obj not in self.object_to_cell:
            return # Object not in grid

        cell_x, cell_y = self.object_to_cell[obj]
        if obj in self.grid[cell_y][cell_x]:
            self.grid[cell_y][cell_x].remove(obj)
        del self.object_to_cell[obj]

    def update_object_position(self, obj: SpatialObject, new_x: float, new_y: float) -> None:
        """Updates an object's position and its location in the grid."""
        old_position = obj.position
        obj.position = (new_x, new_y)

        old_cell_coords = self.object_to_cell.get(obj)
        new_cell_coords = self._get_cell_coords(obj.position)

        if old_cell_coords == new_cell_coords:
            # Object remains in the same cell, no grid update needed beyond position
            return

        if old_cell_coords:
            # Remove from old cell
            old_cell_x, old_cell_y = old_cell_coords
            if obj in self.grid[old_cell_y][old_cell_x]:
                 self.grid[old_cell_y][old_cell_x].remove(obj)
        
        # Add to new cell
        self.grid[new_cell_coords[1]][new_cell_coords[0]].add(obj)
        self.object_to_cell[obj] = new_cell_coords

    def query_nearby(self, position: Tuple[float, float], radius: float) -> List[SpatialObject]:
        """
        Queries for objects within a certain radius of a given position.
        This is a simple square-based query for cells, then filters by actual distance.
        """
        if radius < 0:
            raise ValueError("Radius must be non-negative.")

        center_x, center_y = position
        nearby_objects: Set[SpatialObject] = set()

        # Determine the range of cells to check
        min_x_coord = center_x - radius
        max_x_coord = center_x + radius
        min_y_coord = center_y - radius
        max_y_coord = center_y + radius

        start_cell_x, start_cell_y = self._get_cell_coords((min_x_coord, min_y_coord))
        end_cell_x, end_cell_y = self._get_cell_coords((max_x_coord, max_y_coord))

        for r in range(start_cell_y, end_cell_y + 1):
            for c in range(start_cell_x, end_cell_x + 1):
                # Ensure cell indices are valid (already handled by _get_cell_coords clamping for query point,
                # but good to be mindful if query range could exceed grid)
                if 0 <= r < self.grid_height and 0 <= c < self.grid_width:
                    for obj in self.grid[r][c]:
                        # Actual distance check (squared distance to avoid sqrt)
                        obj_x, obj_y = obj.position
                        dist_sq = (obj_x - center_x)**2 + (obj_y - center_y)**2
                        if dist_sq <= radius**2:
                            nearby_objects.add(obj)
        
        return list(nearby_objects)

    def get_object_cell(self, obj: SpatialObject) -> Tuple[int, int] | None:
        """Returns the (cell_x, cell_y) of an object, or None if not found."""
        return self.object_to_cell.get(obj)

    def get_all_objects_in_cell(self, cell_x: int, cell_y: int) -> Set[SpatialObject]:
        """Returns all objects in a specific cell."""
        if 0 <= cell_y < self.grid_height and 0 <= cell_x < self.grid_width:
            return self.grid[cell_y][cell_x]
        return set()

    def __repr__(self) -> str:
        return f"GridPartition(cell_size={self.cell_size}, grid_dims=({self.grid_width}x{self.grid_height}))"

