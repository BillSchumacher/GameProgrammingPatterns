"""
Tests for the gameloop_ext C extension.
"""

import unittest
import time
import io
import sys

# Attempt to import the extension; skip tests if not available
try:
    import gameloop_ext
except ImportError:
    gameloop_ext = None


@unittest.skipIf(
    gameloop_ext is None,
    "gameloop_ext C extension not built or not found in PYTHONPATH.",
)
class TestGameLoopExtension(unittest.TestCase):
    """Test cases for the GameLoop C extension."""

    def test_initialization(self):
        """Test GameLoop object initialization."""
        loop = gameloop_ext.GameLoop()
        self.assertIsNotNone(loop)
        self.assertFalse(loop.is_running)

        # Test with custom fixed_time_step (actual value not directly readable from Python)
        # We rely on other tests to see its effect.
        loop_custom_ts = gameloop_ext.GameLoop(fixed_time_step=1.0 / 30.0)
        self.assertIsNotNone(loop_custom_ts)
        self.assertFalse(loop_custom_ts.is_running)

    def test_set_handlers_valid_and_none(self):
        """Test setting valid handlers and None."""
        loop = gameloop_ext.GameLoop()

        def dummy_handler_input():
            pass

        def dummy_handler_update(dt):
            pass

        def dummy_handler_render(alpha):
            pass

        loop.set_process_input_handler(dummy_handler_input)
        loop.set_update_handler(dummy_handler_update)
        loop.set_render_handler(dummy_handler_render)

        # Test setting to None (should not error)
        loop.set_process_input_handler(None)
        loop.set_update_handler(None)
        loop.set_render_handler(None)
        self.assertTrue(True)  # If we reached here, it's good.

    def test_set_handlers_type_error(self):
        """Test TypeError for non-callable handlers."""
        loop = gameloop_ext.GameLoop()
        with self.assertRaises(TypeError):
            loop.set_process_input_handler(123)
        with self.assertRaises(TypeError):
            loop.set_update_handler("not a function")
        with self.assertRaises(TypeError):
            loop.set_render_handler(object())

    def test_start_stop_is_running(self):
        """Test the start, stop methods and is_running property."""
        loop = gameloop_ext.GameLoop()
        self.assertFalse(loop.is_running)

        stop_flag = {"called": False}

        def immediate_stop_input():
            # This handler will be called by the loop and stop it.
            if not stop_flag["called"]:
                stop_flag["called"] = True
                loop.stop()

        loop.set_process_input_handler(immediate_stop_input)
        loop.set_update_handler(
            lambda dt: None
        )  # Need some update handler for loop to progress well
        loop.set_render_handler(lambda alpha: None)

        loop.start()  # This is blocking, will return after loop.stop() is called.

        self.assertTrue(stop_flag["called"])
        self.assertFalse(
            loop.is_running, "Loop should be stopped after start() returns."
        )

    def test_callbacks_invoked_with_args(self):
        """Test that Python callbacks are invoked with correct arguments."""
        fixed_fps = 10.0
        loop = gameloop_ext.GameLoop(fixed_time_step=1.0 / fixed_fps)

        callback_data = {
            "input_called_count": 0,
            "update_args": [],
            "render_args": [],
            "max_input_calls": 3,  # Stop after this many input calls
        }

        def py_input():
            callback_data["input_called_count"] += 1
            if callback_data["input_called_count"] >= callback_data["max_input_calls"]:
                loop.stop()

        def py_update(dt):
            callback_data["update_args"].append(dt)

        def py_render(alpha):
            callback_data["render_args"].append(alpha)

        loop.set_process_input_handler(py_input)
        loop.set_update_handler(py_update)
        loop.set_render_handler(py_render)

        loop.start()

        self.assertEqual(
            callback_data["input_called_count"], callback_data["max_input_calls"]
        )

        # Check update calls
        # Adjusted expectation: max_input_calls - 2, because the first frame might not have enough elapsed time
        # and the frame that calls stop() doesn't run its update.
        expected_min_updates = max(0, callback_data["max_input_calls"] - 2)
        self.assertGreaterEqual(
            len(callback_data["update_args"]),
            expected_min_updates,
            f"Should have at least {expected_min_updates} updates",
        )
        if callback_data["update_args"]:
            for dt_arg in callback_data["update_args"]:
                self.assertIsInstance(dt_arg, float)
                self.assertAlmostEqual(
                    dt_arg,
                    1.0 / fixed_fps,
                    places=5,
                    msg="dt should be fixed_time_step",
                )

        # Check render calls
        # Adjusted expectation similarly to updates.
        expected_min_renders = max(0, callback_data["max_input_calls"] - 2)
        self.assertGreaterEqual(
            len(callback_data["render_args"]),
            expected_min_renders,
            f"Should have at least {expected_min_renders} renders",
        )
        if callback_data["render_args"]:
            for alpha_arg in callback_data["render_args"]:
                self.assertIsInstance(alpha_arg, float)
                self.assertTrue(
                    0.0 <= alpha_arg < 1.0,
                    f"Alpha ({alpha_arg}) should be in [0.0, 1.0)",
                )

    def test_loop_runs_with_none_handlers(self):
        """Test that the loop can run and be stopped even with None handlers."""
        loop = gameloop_ext.GameLoop()
        self.assertFalse(loop.is_running)

        stop_flag = {"called": False}

        # Need at least one handler to stop the loop. Let's use input.
        def stop_from_input():
            if not stop_flag["called"]:
                stop_flag["called"] = True
                loop.stop()

        loop.set_process_input_handler(stop_from_input)
        loop.set_update_handler(None)
        loop.set_render_handler(None)

        loop.start()
        self.assertTrue(stop_flag["called"])
        self.assertFalse(loop.is_running)

    def test_callback_exception_handling(self):
        """Test how the loop handles exceptions from Python callbacks."""
        loop = gameloop_ext.GameLoop(fixed_time_step=1.0 / 20.0)  # Faster for test

        exception_raised_in_input = False
        update_calls_after_exception = 0
        max_updates_post_exception = 2

        def faulty_input_handler():
            nonlocal exception_raised_in_input
            # This handler will be called first, raise an exception.
            if not exception_raised_in_input:  # Raise only once
                exception_raised_in_input = True
                raise ValueError("Test exception in input handler")
            # If called again, stop the loop (should not happen if error stops processing for this handler)
            # loop.stop()

        def update_handler_post_exception(_dt):
            nonlocal update_calls_after_exception
            if (
                exception_raised_in_input
            ):  # Start counting only after input tried to raise
                update_calls_after_exception += 1
            if update_calls_after_exception >= max_updates_post_exception:
                loop.stop()  # Stop after a few updates post-exception

        loop.set_process_input_handler(faulty_input_handler)
        loop.set_update_handler(update_handler_post_exception)
        loop.set_render_handler(lambda alpha: None)  # Add a render handler

        old_stderr = sys.stderr
        sys.stderr = captured_stderr = io.StringIO()

        try:
            loop.start()
        finally:
            sys.stderr = old_stderr  # Restore stderr

        self.assertTrue(
            exception_raised_in_input, "Faulty handler should have been called."
        )
        # Check if the loop continued enough for update_handler_post_exception to stop it
        self.assertGreaterEqual(
            update_calls_after_exception,
            max_updates_post_exception,
            "Loop should continue for a few updates after exception in one callback.",
        )

        error_output = captured_stderr.getvalue()
        self.assertIn(
            "ValueError: Test exception in input handler",
            error_output,
            "Stderr should contain the exception.",
        )
        self.assertIn(
            "Traceback (most recent call last):",
            error_output,
            "Stderr should contain Python traceback.",
        )
        self.assertFalse(
            loop.is_running, "Loop should be stopped by the update handler."
        )


if __name__ == "__main__":
    # Ensure gameloop_ext can be imported from the project root if tests are run directly
    # This might be needed if the CWD is tests/ and the .pyd is in the parent dir.
    # However, `python -m unittest discover tests` from root should handle this.
    unittest.main()
