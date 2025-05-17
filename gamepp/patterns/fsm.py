from abc import ABC, abstractmethod
from typing import Any, Dict, Type


class State(ABC):
    """
    Abstract base class for all states in the FSM.
    Each state has a reference to the context (StateMachine).
    """

    def __init__(self, context: "StateMachine"):
        self._context = context

    @property
    def context(self) -> "StateMachine":
        return self._context

    def enter(self, **kwargs) -> None:
        """
        Called when entering this state.
        kwargs can be used to pass dynamic parameters upon entry.
        """
        pass

    def exit(self) -> None:
        """Called when exiting this state."""
        pass

    @abstractmethod
    def update(self, event: Any = None) -> None:
        """
        Called to update the state, potentially triggering a transition.
        'event' can be any data relevant to the state's logic.
        """
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


class StateMachine:
    """
    The Finite State Machine.
    Manages states and transitions.
    """

    def __init__(
        self,
        initial_state_class: Type[State],
        constructor_kwargs: Dict[str, Any] = None,
        enter_kwargs: Dict[str, Any] = None,
    ):
        self._current_state: State = None
        self._states: Dict[Type[State], State] = {}  # Cache for state instances

        if constructor_kwargs is None:
            constructor_kwargs = {}
        if enter_kwargs is None:
            enter_kwargs = {}

        # Initialize the first state
        self.change_state(
            initial_state_class,
            constructor_kwargs=constructor_kwargs,
            enter_kwargs=enter_kwargs,
        )

    def _get_or_create_state(
        self, state_class: Type[State], **constructor_kwargs: Any
    ) -> State:
        """
        Retrieves an existing state instance or creates a new one.
        If the state is created, constructor_kwargs are passed to its __init__.
        """
        if state_class not in self._states:
            print(
                f"FSM: Creating new instance of {state_class.__name__} with constructor_kwargs: {constructor_kwargs}"
            )
            self._states[state_class] = state_class(self, **constructor_kwargs)
        else:
            # Don't print if constructor_kwargs is empty and state exists, to reduce noise
            if constructor_kwargs:
                print(
                    f"FSM: Using cached instance of {state_class.__name__}. Constructor_kwargs {constructor_kwargs} ignored for existing instance."
                )
            else:
                print(f"FSM: Using cached instance of {state_class.__name__}.")
        return self._states[state_class]

    def change_state(
        self,
        new_state_class: Type[State],
        constructor_kwargs: Dict[str, Any] = None,
        enter_kwargs: Dict[str, Any] = None,
    ) -> None:
        """
        Changes the current state of the FSM.
        Calls exit() on the old state and enter() on the new state.
        `constructor_kwargs` are for the state's __init__ (if created).
        `enter_kwargs` are for the state's enter() method.
        """
        if constructor_kwargs is None:
            constructor_kwargs = {}
        if enter_kwargs is None:
            enter_kwargs = {}

        if self._current_state:
            # print(f"FSM: Exiting {self._current_state}") # Verbose
            self._current_state.exit()

        new_state_instance = self._get_or_create_state(
            new_state_class, **constructor_kwargs
        )

        # print(f"FSM: Entering {new_state_instance} with enter_kwargs: {enter_kwargs}") # Verbose
        self._current_state = new_state_instance
        self._current_state.enter(**enter_kwargs)

    def update(self, event: Any = None) -> None:
        """
        Delegates the update call to the current state.
        """
        if self._current_state:
            self._current_state.update(event)
        else:
            print(
                "FSM: No current state to update."
            )  # Should not happen in a well-initialized FSM

    @property
    def current_state(self) -> State:
        return self._current_state

    def __str__(self) -> str:
        return f"StateMachine(current_state={self._current_state})"
