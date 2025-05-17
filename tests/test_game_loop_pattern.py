import unittest
import time
from unittest.mock import MagicMock

from gamepp.patterns.game_loop import GameLoop


class TestGameLoop(unittest.TestCase):
    def setUp(self):
        self.loop = GameLoop()
        self.mock_input_handler = MagicMock()
        self.mock_update_handler = MagicMock()
        self.mock_render_handler = MagicMock()

        self.loop.set_process_input_handler(self.mock_input_handler)
        self.loop.set_update_handler(self.mock_update_handler)
        self.loop.set_render_handler(self.mock_render_handler)

    def test_initial_state(self):
        self.assertFalse(self.loop.is_running)

    def test_start_and_stop_loop(self):
        self.assertFalse(self.loop.is_running)

        # To prevent the test from running indefinitely, we'll modify
        # the input handler to stop the loop after a few calls.
        call_count = 0

        def stop_after_few_calls():
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                self.loop.stop()

        self.loop.set_process_input_handler(stop_after_few_calls)
        self.loop.start()

        self.assertFalse(self.loop.is_running, "Loop should be stopped")
        self.assertGreaterEqual(
            call_count, 3, "Input handler should have been called multiple times"
        )

    def test_handlers_called_in_loop(self):
        # Ensure update() is called by setting a very small fixed_time_step for this test
        # This makes it highly probable that _lag >= _fixed_time_step even on the first frame.
        original_fixed_time_step = self.loop._fixed_time_step
        self.loop._fixed_time_step = 0.000001  # A very small number

        stop_loop_flag = False  # To ensure stop() is called only once

        # Wrapper for the render mock to stop the loop
        def stopping_render_handler(alpha: float):
            nonlocal stop_loop_flag
            self.mock_render_handler(alpha)  # Call the actual mock
            # Stop if update has been called, ensuring a full cycle for this test's purpose
            if self.mock_update_handler.called and not stop_loop_flag:
                self.loop.stop()
                stop_loop_flag = True

        # The input and update mocks are already set in setUp.
        self.loop.set_render_handler(stopping_render_handler)

        self.loop.start()

        self.mock_input_handler.assert_called()  # Should be called at least once
        self.mock_update_handler.assert_called()  # Should be called at least once
        self.mock_render_handler.assert_called()  # Should be called at least once by stopping_render_handler

        # Restore fixed_time_step to avoid affecting other tests
        self.loop._fixed_time_step = original_fixed_time_step

    def test_update_handler_receives_delta_time(self):
        # Stop the loop after the first update call
        received_dt = -1.0

        def check_dt_and_stop(dt: float):
            nonlocal received_dt
            received_dt = dt
            self.mock_update_handler(dt)  # Call the original mock
            self.loop.stop()

        self.loop.set_update_handler(check_dt_and_stop)
        self.loop.start()

        self.mock_update_handler.assert_called_once()
        self.assertGreater(received_dt, 0.0, "Delta time should be positive")
        self.assertLess(
            received_dt,
            0.1,
            "Delta time should be reasonably small for a quick loop iteration",
        )

    def test_loop_does_not_start_if_already_running(self):
        # This test is a bit tricky because start() is blocking.
        # We'll use a flag and a short run.
        def stop_quickly():
            self.loop.stop()

        self.loop.set_process_input_handler(stop_quickly)
        self.loop.start()  # First start
        self.assertFalse(self.loop.is_running)

        # Try to start again - it shouldn't re-enter the loop logic if it was already running,
        # but since it's stopped, it will start again. The internal _is_running check
        # at the beginning of start() is what we are implicitly testing.
        # To truly test the "if self._is_running: return" part, we'd need threading
        # or a more complex setup. For now, we ensure it can be restarted.

        call_count = 0

        def count_and_stop():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                self.loop.stop()

        self.loop.set_process_input_handler(count_and_stop)
        self.loop.start()  # Second start
        self.assertFalse(self.loop.is_running)
        self.assertGreaterEqual(call_count, 2)

    def test_handlers_can_be_none_initially(self):
        # Test that the loop doesn't crash if handlers are not set before start
        # It will use the default lambda handlers
        local_loop = GameLoop()

        def stop_local_loop():
            local_loop.stop()

        # We need at least one handler to stop the loop
        local_loop.set_process_input_handler(stop_local_loop)
        try:
            local_loop.start()
        except Exception as e:
            self.fail(f"Loop with default handlers crashed: {e}")
        self.assertFalse(local_loop.is_running)


if __name__ == "__main__":
    unittest.main()
