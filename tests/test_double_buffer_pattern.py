import unittest
from gamepp.patterns.double_buffer import Buffer, DoubleBuffer


class TestBuffer(unittest.TestCase):
    def test_buffer_creation(self):
        buffer = Buffer[int](10, 5)
        self.assertEqual(buffer.width, 10)
        self.assertEqual(buffer.height, 5)
        for y in range(5):
            for x in range(10):
                self.assertIsNone(buffer.get_pixel(x, y))

    def test_buffer_creation_invalid_dimensions(self):
        with self.assertRaises(ValueError):
            Buffer[int](0, 5)
        with self.assertRaises(ValueError):
            Buffer[int](10, 0)
        with self.assertRaises(ValueError):
            Buffer[int](-1, 5)

    def test_buffer_clear(self):
        buffer = Buffer[str](2, 2)
        buffer.draw(0, 0, "A")
        buffer.draw(1, 1, "B")
        buffer.clear("X")
        self.assertEqual(buffer.get_pixel(0, 0), "X")
        self.assertEqual(buffer.get_pixel(0, 1), "X")
        self.assertEqual(buffer.get_pixel(1, 0), "X")
        self.assertEqual(buffer.get_pixel(1, 1), "X")

    def test_buffer_draw_and_get_pixel(self):
        buffer = Buffer[int](3, 3)
        buffer.draw(1, 1, 100)
        self.assertEqual(buffer.get_pixel(1, 1), 100)
        self.assertIsNone(buffer.get_pixel(0, 0))

    def test_buffer_draw_out_of_bounds(self):
        buffer = Buffer[int](2, 2)
        buffer.draw(-1, 0, 1)  # Should be ignored
        buffer.draw(0, -1, 2)  # Should be ignored
        buffer.draw(2, 0, 3)  # Should be ignored
        buffer.draw(0, 2, 4)  # Should be ignored
        self.assertIsNone(buffer.get_pixel(-1, 0))
        self.assertIsNone(buffer.get_pixel(0, -1))
        self.assertIsNone(buffer.get_pixel(2, 0))
        self.assertIsNone(buffer.get_pixel(0, 2))
        # Check that valid pixels are not affected
        buffer.draw(0, 0, 5)
        self.assertEqual(buffer.get_pixel(0, 0), 5)

    def test_buffer_get_pixel_out_of_bounds(self):
        buffer = Buffer[int](2, 2)
        self.assertIsNone(buffer.get_pixel(-1, 0))
        self.assertIsNone(buffer.get_pixel(0, -1))
        self.assertIsNone(buffer.get_pixel(2, 0))
        self.assertIsNone(buffer.get_pixel(0, 2))


class TestDoubleBuffer(unittest.TestCase):
    def test_double_buffer_creation(self):
        db = DoubleBuffer[int](10, 8)
        self.assertEqual(db.get_width(), 10)
        self.assertEqual(db.get_height(), 8)
        self.assertIsInstance(db.current_buffer, Buffer)
        self.assertIsInstance(db.draw_buffer, Buffer)
        self.assertNotEqual(id(db.current_buffer), id(db.draw_buffer))
        self.assertEqual(db.current_buffer.width, 10)
        self.assertEqual(db.current_buffer.height, 8)
        self.assertEqual(db.draw_buffer.width, 10)
        self.assertEqual(db.draw_buffer.height, 8)

    def test_double_buffer_creation_invalid_dimensions(self):
        with self.assertRaises(ValueError):
            DoubleBuffer[int](0, 5)
        with self.assertRaises(ValueError):
            DoubleBuffer[int](10, 0)
        with self.assertRaises(ValueError):
            DoubleBuffer[int](-1, 5)

    def test_swap_buffers(self):
        db = DoubleBuffer[str](2, 1)
        initial_front = db.current_buffer
        initial_back = db.draw_buffer

        db.draw_buffer.draw(0, 0, "A")
        db.draw_buffer.draw(1, 0, "B")

        self.assertIsNone(db.current_buffer.get_pixel(0, 0))

        db.swap_buffers()

        self.assertIs(db.current_buffer, initial_back)
        self.assertIs(db.draw_buffer, initial_front)
        self.assertEqual(db.current_buffer.get_pixel(0, 0), "A")
        self.assertEqual(db.current_buffer.get_pixel(1, 0), "B")
        self.assertIsNone(
            db.draw_buffer.get_pixel(0, 0)
        )  # Old front buffer should be clean or irrelevant

    def test_clear_draw_buffer(self):
        db = DoubleBuffer[int](2, 2)
        db.draw_buffer.draw(0, 0, 1)
        db.draw_buffer.draw(1, 1, 2)

        db.clear_draw_buffer(0)

        self.assertEqual(db.draw_buffer.get_pixel(0, 0), 0)
        self.assertEqual(db.draw_buffer.get_pixel(0, 1), 0)
        self.assertEqual(db.draw_buffer.get_pixel(1, 0), 0)
        self.assertEqual(db.draw_buffer.get_pixel(1, 1), 0)

        # Ensure current_buffer is not affected
        self.assertIsNone(db.current_buffer.get_pixel(0, 0))

    def test_drawing_and_swapping_flow(self):
        db = DoubleBuffer[str](3, 1)

        # Frame 1: Draw to back buffer
        db.draw_buffer.draw(0, 0, "F1_0")
        db.draw_buffer.draw(1, 0, "F1_1")

        # Before swap, front buffer is empty
        self.assertIsNone(db.current_buffer.get_pixel(0, 0))

        db.swap_buffers()

        # After swap, front buffer has Frame 1 content
        self.assertEqual(db.current_buffer.get_pixel(0, 0), "F1_0")
        self.assertEqual(db.current_buffer.get_pixel(1, 0), "F1_1")

        # Frame 2: Draw to new back buffer (old front buffer)
        db.clear_draw_buffer()  # Clear the (now) back buffer
        db.draw_buffer.draw(0, 0, "F2_0")
        db.draw_buffer.draw(2, 0, "F2_2")

        # Front buffer still shows Frame 1 content
        self.assertEqual(db.current_buffer.get_pixel(0, 0), "F1_0")
        self.assertEqual(db.current_buffer.get_pixel(1, 0), "F1_1")
        self.assertIsNone(db.current_buffer.get_pixel(2, 0))

        db.swap_buffers()

        # After swap, front buffer has Frame 2 content
        self.assertEqual(db.current_buffer.get_pixel(0, 0), "F2_0")
        self.assertIsNone(db.current_buffer.get_pixel(1, 0))  # This pixel was cleared
        self.assertEqual(db.current_buffer.get_pixel(2, 0), "F2_2")


if __name__ == "__main__":
    unittest.main()
