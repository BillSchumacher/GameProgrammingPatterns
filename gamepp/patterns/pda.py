from typing import List, Any, Optional

class PDAState:
    """
    Base class for states in a Pushdown Automaton.
    """
    def handle_input(self, pda: 'PushdownAutomata', input_data: Any) -> None:
        """
        Handles input for the state.
        Can call pda.push_state() or pda.pop_state() to change the PDA's state.
        """
        pass

    def enter(self, pda: 'PushdownAutomata') -> None:
        """Called when the state is entered (pushed onto the stack)."""
        pass

    def exit(self, pda: 'PushdownAutomata') -> None:
        """Called when the state is exited (popped from the stack)."""
        pass

class PushdownAutomata:
    """
    Pushdown Automaton (PDA)
    Manages a stack of states. Input is handled by the state at the top of the stack.
    When a state is finished, it can be popped, and the PDA returns to the previous state.
    """
    def __init__(self, initial_state: Optional[PDAState] = None):
        self._stack: List[PDAState] = []
        if initial_state:
            self.push_state(initial_state)

    def push_state(self, state: PDAState) -> None:
        """Pushes a new state onto the stack and calls its enter() method."""
        self._stack.append(state)
        state.enter(self)

    def pop_state(self) -> Optional[PDAState]:
        """
        Pops the current state from the stack and calls its exit() method.
        Returns the popped state or None if the stack was empty.
        """
        if not self._stack:
            return None
        
        current_state = self._stack.pop()
        current_state.exit(self)
        
        return current_state

    def handle_input(self, input_data: Any) -> None:
        """
        Passes input data to the current state (top of the stack).
        """
        if self.current_state:
            self.current_state.handle_input(self, input_data)

    @property
    def current_state(self) -> Optional[PDAState]:
        """Returns the current state (top of the stack) without removing it."""
        if not self._stack:
            return None
        return self._stack[-1]

    @property
    def stack_depth(self) -> int:
        """Returns the current depth of the state stack."""
        return len(self._stack)
