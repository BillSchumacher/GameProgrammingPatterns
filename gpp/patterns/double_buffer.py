\
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class Buffer(Generic[T]):
    """
    Represents a single buffer that stores pixel data or any other 2D grid data.
    """
    def __init__(self, width: int, height: int):
        if width <= 0 or height <= 0:
            raise ValueError("Buffer dimensions must be positive.")
        self.width = width
        self.height = height
        self._pixels: List[List[Optional[T]]] = [[None for _ in range(width)] for _ in range(height)]

    def clear(self, value: Optional[T] = None) -> None:
        """Clears the buffer, setting all pixels to the given value."""
        for y in range(self.height):
            for x in range(self.width):
                self._pixels[y][x] = value

    def draw(self, x: int, y: int, value: T) -> None:
        """Sets the pixel at (x, y) to the given value."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self._pixels[y][x] = value
        # Optionally, raise an error or handle out-of-bounds drawing as needed.
        # For now, it silently ignores out-of-bounds draws.

    def get_pixel(self, x: int, y: int) -> Optional[T]:
        """Gets the pixel at (x, y). Returns None if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._pixels[y][x]
        return None

    def __repr__(self) -> str:
        return f"<Buffer ({self.width}x{self.height})>"


class DoubleBuffer(Generic[T]):
    """
    Manages two buffers (a front buffer for reading/display and a back buffer for drawing)
    to prevent tearing and provide smoother updates.
    """
    def __init__(self, width: int, height: int):
        if width <= 0 or height <= 0:
            raise ValueError("DoubleBuffer dimensions must be positive.")
        self._front_buffer = Buffer[T](width, height)
        self._back_buffer = Buffer[T](width, height)

    @property
    def current_buffer(self) -> Buffer[T]:
        """
        The buffer currently intended for display or reading.
        This is the "front" buffer.
        """
        return self._front_buffer

    @property
    def draw_buffer(self) -> Buffer[T]:
        """
        The buffer intended for drawing operations.
        This is the "back" buffer.
        """
        return self._back_buffer

    def swap_buffers(self) -> None:
        """
        Swaps the front and back buffers. The content previously in the draw_buffer
        becomes the content of the current_buffer, and the old current_buffer
        becomes the new draw_buffer (and is typically cleared or overwritten).
        """
        self._front_buffer, self._back_buffer = self._back_buffer, self._front_buffer

    def clear_draw_buffer(self, value: Optional[T] = None) -> None:
        """Clears the draw buffer (the back buffer)."""
        self.draw_buffer.clear(value)

    def get_width(self) -> int:
        """Returns the width of the buffers."""
        return self._front_buffer.width # Both buffers have the same dimensions

    def get_height(self) -> int:
        """Returns the height of the buffers."""
        return self._front_buffer.height # Both buffers have the same dimensions

    def __repr__(self) -> str:
        return f"<DoubleBuffer ({self.get_width()}x{self.get_height()})>"
