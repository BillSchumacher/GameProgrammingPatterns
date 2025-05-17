from typing import List, Any


class StateMachineInterface:
    """
    A simple interface for a state machine that can handle input.
    """

    def handle_input(self, input_data: Any) -> None:
        raise NotImplementedError


class CSM:
    """
    Concurrent State Machine (CSM)
    Manages a collection of state machines and passes input to all of them.
    """

    def __init__(self):
        self._state_machines: List[StateMachineInterface] = []

    def add_state_machine(self, sm: StateMachineInterface) -> None:
        """Adds a state machine to the CSM."""
        if not hasattr(sm, "handle_input") or not callable(sm.handle_input):
            raise ValueError(
                "State machine must have a callable 'handle_input' method."
            )
        if sm not in self._state_machines:
            self._state_machines.append(sm)

    def remove_state_machine(self, sm: StateMachineInterface) -> None:
        """Removes a state machine from the CSM."""
        if sm in self._state_machines:
            self._state_machines.remove(sm)

    def handle_input(self, input_data: Any) -> None:
        """Passes the input data to all managed state machines."""
        for sm in self._state_machines:
            sm.handle_input(input_data)

    @property
    def state_machines(self) -> List[StateMachineInterface]:
        return self._state_machines
