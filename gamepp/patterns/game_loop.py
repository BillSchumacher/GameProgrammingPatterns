import time
from typing import Callable

class GameLoop:
    """
    Implements the Game Loop pattern.

    The game loop runs continuously during gameplay. Each turn of the loop,
    it processes user input without blocking, updates the game state, and
    renders the game. It tracks the passage of time to control the rate of
    gameplay.
    """
    def __init__(self, fixed_time_step: float = 1/60): # Default to 60 updates per second
        self._is_running = False
        self._last_time = 0.0
        self.process_input: Callable[[], None] = lambda: None
        self.update: Callable[[float], None] = lambda dt: None
        self.render: Callable[[float], None] = lambda alpha: None
        self._fixed_time_step: float = fixed_time_step
        self._lag: float = 0.0

    def start(self) -> None:
        """Starts the game loop with a fixed time step for updates."""
        if self._is_running:
            return

        self._is_running = True
        self._last_time = time.perf_counter()
        self._lag = 0.0 # Reset lag when starting

        while self._is_running:
            current_time = time.perf_counter()
            elapsed_time = current_time - self._last_time
            self._last_time = current_time
            self._lag += elapsed_time

            self.process_input()

            # Update game logic in fixed time steps
            while self._lag >= self._fixed_time_step:
                self.update(self._fixed_time_step)
                self._lag -= self._fixed_time_step

            self.render(self._lag / self._fixed_time_step) # Useful for interpolating rendering

            # Optional: Add a small sleep to prevent hogging CPU if updates are too fast
            # and to yield time to other processes.
            # This can be more sophisticated, e.g., sleeping for the remaining time
            # until the next expected frame if VSync or a target FPS is desired.
            # For now, a minimal sleep if no updates happened can be useful.
            if elapsed_time < self._fixed_time_step: # Heuristic: if we are running faster than updates
                sleep_time = self._fixed_time_step - self._lag if self._lag < self._fixed_time_step else 0.001
                if sleep_time > 0:
                    time.sleep(sleep_time)

    def stop(self) -> None:
        """Stops the game loop."""
        self._is_running = False

    def set_process_input_handler(self, handler: Callable[[], None]) -> None:
        """Sets the handler for processing input."""
        self.process_input = handler

    def set_update_handler(self, handler: Callable[[float], None]) -> None:
        """Sets the handler for updating game state."""
        self.update = handler

    def set_render_handler(self, handler: Callable[[float], None]) -> None:
        """Sets the handler for rendering the game."""
        self.render = handler

    @property
    def is_running(self) -> bool:
        """Returns True if the game loop is currently running, False otherwise."""
        return self._is_running

if __name__ == '__main__':
    # Example Usage
    loop = GameLoop(fixed_time_step=1/60) # 60 updates per second

    processed_updates = 0 # Counter for example
    current_position = 0
    previous_position = 0
    speed = 10 # units per second

    def my_input():
        print("Processing input...")
        # In a real game, you might check for key presses, mouse movements, etc.
        # For this example, let's stop the loop after a certain number of updates.
        if processed_updates >= 5: # Stop after 5 game updates
            loop.stop()

    def my_update(dt: float):
        global processed_updates, current_position, previous_position
        previous_position = current_position
        current_position += speed * dt # Simulate movement
        processed_updates += 1
        print(f"Updating game state with fixed_time_step: {dt:.4f}s (Update #{processed_updates}), Pos: {current_position:.2f}")

    def my_render(alpha: float):
        # Interpolate position for smoother rendering
        interpolated_position = previous_position * (1.0 - alpha) + current_position * alpha
        print(f"Rendering game... Alpha: {alpha:.2f}, Interpolated Pos: {interpolated_position:.2f}")
        print("-" * 20)

    loop.set_process_input_handler(my_input)
    loop.set_update_handler(my_update)
    loop.set_render_handler(my_render)

    print("Starting game loop with fixed time step...")
    loop.start()
    print("Game loop stopped.")
