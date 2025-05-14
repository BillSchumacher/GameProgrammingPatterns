import unittest
from unittest.mock import MagicMock, call
from typing import Any
from gpp.patterns.fsm import State, StateMachine


class IdleState(State):
    def __init__(self, context: 'StateMachine', id_prefix="Idle"):
        super().__init__(context)
        self.id_prefix = id_prefix # Example constructor arg
        self.entered_with_reason = None
        self.exit_called = False
        # print(f"{self}: Initialized with id_prefix '{self.id_prefix}'.") # For debug

    def enter(self, **kwargs):
        self.entered_with_reason = kwargs.get("reason", "activity ended")
        # print(f"{self}: Player is idling (reason: {self.entered_with_reason}). Waiting for action.")

    def update(self, event: Any = None):
        if event == "walk_command":
            # print(f"{self}: Received walk_command.")
            self.context.change_state(WalkingState) 
        elif event == "jump_command":
            # print(f"{self}: Received jump_command.")
            self.context.change_state(JumpingState)

    def exit(self):
        self.exit_called = True
        # print(f"{self}: No longer idling.")

class WalkingState(State):
    def __init__(self, context: 'StateMachine', initial_speed: int = 5):
        super().__init__(context)
        self.base_speed = initial_speed 
        self.current_speed = initial_speed
        self.steps_taken = 0
        self.entered_with_speed = None
        self.exit_called = False
        # print(f"{self}: Initialized with base_speed {self.base_speed}.")

    def enter(self, **kwargs):
        self.entered_with_speed = kwargs.get("speed", self.base_speed)
        self.current_speed = self.entered_with_speed
        self.steps_taken = 0 
        # print(f"{self}: Player started walking at speed {self.current_speed}.")

    def update(self, event: Any = None):
        if event == "stop_command":
            # print(f"{self}: Received stop_command.")
            self.context.change_state(IdleState, enter_kwargs={'reason': "stopped walking"})
        elif event == "jump_command":
            # print(f"{self}: Received jump_command while walking.")
            self.context.change_state(JumpingState)
        else:
            self.steps_taken += 1

    def exit(self):
        self.exit_called = True
        # print(f"{self}: Player stopped walking after {self.steps_taken} steps.")

class JumpingState(State):
    def __init__(self, context: 'StateMachine', initial_height: int = 10):
        super().__init__(context)
        self.base_jump_height = initial_height
        self.current_jump_height = initial_height
        self.air_time = 0
        self.entered_with_height = None
        self.exit_called = False
        # print(f"{self}: Initialized with base_jump_height {self.base_jump_height}.")

    def enter(self, **kwargs):
        self.entered_with_height = kwargs.get("height", self.base_jump_height)
        self.current_jump_height = self.entered_with_height
        self.air_time = 0
        # print(f"{self}: Player started jumping to height {self.current_jump_height}.")

    def update(self, event: Any = None):
        self.air_time += 1
        if self.air_time >= self.current_jump_height / 2: 
            # print(f"{self}: Player is landing.")
            self.context.change_state(IdleState, enter_kwargs={'reason': "landed from jump"})

    def exit(self):
        self.exit_called = True
        # print(f"{self}: Player landed after {self.air_time} air time units.")

class TestFiniteStateMachine(unittest.TestCase):

    def test_initial_state_and_entry_params(self):
        fsm = StateMachine(IdleState, enter_kwargs={'reason': "Game Start"})
        self.assertIsInstance(fsm.current_state, IdleState)
        self.assertEqual(fsm.current_state.entered_with_reason, "Game Start")

    def test_event_transitions(self):
        fsm = StateMachine(IdleState, enter_kwargs={'reason': "Initial"})
        idle_state_instance = fsm.current_state

        fsm.update("walk_command")
        self.assertIsInstance(fsm.current_state, WalkingState)
        self.assertTrue(idle_state_instance.exit_called)
        self.assertEqual(fsm.current_state.entered_with_speed, 5) # Default initial_speed and enter speed

        walking_state_instance = fsm.current_state
        fsm.update("jump_command")
        self.assertIsInstance(fsm.current_state, JumpingState)
        self.assertTrue(walking_state_instance.exit_called)
        self.assertEqual(fsm.current_state.entered_with_height, 10) # Default initial_height and enter height

        jumping_state_instance = fsm.current_state
        # Simulate updates until landing
        for _ in range(5): # Default height 10, lands when air_time >= 5
            fsm.update()
            if isinstance(fsm.current_state, IdleState):
                break
        self.assertIsInstance(fsm.current_state, IdleState)
        self.assertTrue(jumping_state_instance.exit_called)
        self.assertEqual(fsm.current_state.entered_with_reason, "landed from jump")

    def test_change_state_with_constructor_and_enter_kwargs(self):
        fsm = StateMachine(IdleState)
        idle_state_instance = fsm.current_state

        # Change to WalkingState, providing kwargs for its constructor and enter method
        fsm.change_state(WalkingState, 
                         constructor_kwargs={'initial_speed': 7}, 
                         enter_kwargs={'speed': 10})
        
        self.assertIsInstance(fsm.current_state, WalkingState)
        self.assertTrue(idle_state_instance.exit_called)
        self.assertEqual(fsm.current_state.base_speed, 7) # From constructor_kwargs
        self.assertEqual(fsm.current_state.current_speed, 10) # From enter_kwargs
        self.assertEqual(fsm.current_state.entered_with_speed, 10)

        # Change back to Idle, then to WalkingState again to test caching
        # The constructor_kwargs for WalkingState should be ignored this time.
        walking_state_instance_first = fsm.current_state
        fsm.change_state(IdleState, enter_kwargs={'reason': "Temp Idle"})
        idle_state_instance_2 = fsm.current_state

        fsm.change_state(WalkingState, 
                         constructor_kwargs={'initial_speed': 99}, # Should be ignored
                         enter_kwargs={'speed': 12})
        self.assertIsInstance(fsm.current_state, WalkingState)
        self.assertTrue(idle_state_instance_2.exit_called)
        self.assertIs(fsm.current_state, walking_state_instance_first, "Should reuse cached WalkingState instance")
        self.assertEqual(fsm.current_state.base_speed, 7) # Should retain original base_speed
        self.assertEqual(fsm.current_state.current_speed, 12) # New enter speed
        self.assertEqual(fsm.current_state.entered_with_speed, 12)

    def test_fsm_initialization_with_state_constructor_and_enter_kwargs(self):
        fsm = StateMachine(WalkingState, 
                           constructor_kwargs={'initial_speed': 3}, 
                           enter_kwargs={'speed': 4})
        self.assertIsInstance(fsm.current_state, WalkingState)
        self.assertEqual(fsm.current_state.base_speed, 3)
        self.assertEqual(fsm.current_state.current_speed, 4)
        self.assertEqual(fsm.current_state.entered_with_speed, 4)

        walking_state_instance = fsm.current_state
        fsm.update("stop_command")
        self.assertIsInstance(fsm.current_state, IdleState)
        self.assertTrue(walking_state_instance.exit_called)
        self.assertEqual(fsm.current_state.entered_with_reason, "stopped walking")

    def test_state_str_representation(self):
        idle = IdleState(MagicMock()) # Pass a mock context
        self.assertEqual(str(idle), "IdleState")
        walking = WalkingState(MagicMock())
        self.assertEqual(str(walking), "WalkingState")

if __name__ == "__main__":
    unittest.main()
