from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional, List

class HState(ABC):
    """
    Abstract base class for a state in a Hierarchical State Machine.
    """
    default_child_state_class: Optional[Type['HState']] = None # ADDED: For type hinting and default access pattern

    def __init__(self, context: 'HStateMachine', parent: Optional['HState'] = None, **kwargs):
        self._context: 'HStateMachine' = context
        self._parent: Optional['HState'] = parent
        self._active_sub_state_instance: Optional['HState'] = None
        # kwargs are passed from HStateMachine._get_or_create_instance
        # Concrete states can use them in their __init__ after super().__init__

    @property
    def context(self) -> 'HStateMachine':
        return self._context

    @property
    def parent(self) -> Optional['HState']:
        return self._parent

    @property
    def active_sub_state_instance(self) -> Optional['HState']:
        return self._active_sub_state_instance

    # --- Methods for concrete states to override ---

    def get_initial_sub_state_class(self) -> Optional[Type['HState']]:
        """If this state is a super-state, override to return the class of its initial sub-state.
           By default, returns the 'default_child_state_class' attribute set on the class.
        """
        return self.default_child_state_class # MODIFIED: Return the class attribute

    def on_enter(self, **kwargs) -> None:
        """Called when this specific state is entered. kwargs are passed from transition logic."""
        pass

    def on_exit(self, **kwargs) -> None:
        """Called when this specific state is exited. kwargs are passed from transition logic."""
        pass

    @abstractmethod
    def on_handle_event(self, event: Any, **kwargs) -> bool:
        """
        Process an event locally for this state. 
        Return True if handled (event propagation stops), False otherwise.
        This method can trigger a state transition using self.context.transition_to(...).
        kwargs are passed from HStateMachine.dispatch().
        """
        pass

    # --- Internal methods called by HStateMachine or other HStates ---

    def _enter_state_internal(self, enter_kwargs_for_self: Dict[str, Any], 
                              constructor_kwargs_map: Dict[Type['HState'], Dict[str, Any]],
                              enter_kwargs_map_for_subs: Dict[Type['HState'], Dict[str, Any]]) -> 'HState':
        """
        Internal method to handle the full entry process for this state and its initial sub-states.
        Returns the leaf state that was ultimately entered.
        """
        # print(f"HSM_DEBUG: Entering {self.__class__.__name__} with {enter_kwargs_for_self}")
        self.on_enter(**enter_kwargs_for_self)
        
        initial_sub_class = self.get_initial_sub_state_class()
        if initial_sub_class:
            # print(f"HSM_DEBUG: {self.__class__.__name__} has initial sub-state {initial_sub_class.__name__}")
            sub_constructor_kwargs = constructor_kwargs_map.get(initial_sub_class, {})
            direct_sub_instance = self.context._get_or_create_instance(initial_sub_class, self, sub_constructor_kwargs)
            self._active_sub_state_instance = direct_sub_instance
            
            sub_enter_kwargs = enter_kwargs_map_for_subs.get(initial_sub_class, {})
            return direct_sub_instance._enter_state_internal(sub_enter_kwargs, constructor_kwargs_map, enter_kwargs_map_for_subs)
        return self # This state is the leaf in this branch

    def _exit_state_internal(self, exit_kwargs_for_self: Dict[str, Any], exit_kwargs_map_for_subs: Dict[Type['HState'], Dict[str, Any]]) -> None:
        """Internal method to handle the full exit process for this state and its active sub-states."""
        if self._active_sub_state_instance:
            # print(f"HSM_DEBUG: {self.__class__.__name__} exiting active sub-state {self._active_sub_state_instance.__class__.__name__}")
            sub_exit_kwargs = exit_kwargs_map_for_subs.get(self._active_sub_state_instance.__class__, {})
            self._active_sub_state_instance._exit_state_internal(sub_exit_kwargs, exit_kwargs_map_for_subs)
            self._active_sub_state_instance = None
        
        # print(f"HSM_DEBUG: Exiting {self.__class__.__name__} with {exit_kwargs_for_self}")
        self.on_exit(**exit_kwargs_for_self)

    def _handle_event_internal(self, event: Any, event_dispatch_kwargs: Dict[str, Any]) -> bool:
        """
        Internal method to handle event dispatch hierarchically.
        Sub-state gets first chance, then this state.
        """
        if self._active_sub_state_instance:
            if self._active_sub_state_instance._handle_event_internal(event, event_dispatch_kwargs):
                return True
        
        return self.on_handle_event(event, **event_dispatch_kwargs)

    def __str__(self) -> str:
        return self.__class__.__name__

class HStateMachine:
    def __init__(self, logger: Optional[Any] = None): # MODIFIED: Accept and store logger
        self._current_leaf_instance: Optional[HState] = None
        self._active_states_path: List[HState] = []
        self._instance_cache: Dict[Type[HState], HState] = {}
        self._is_transitioning: bool = False
        self.hsm_logger = logger # Stored, can be used by HSM or as a default for states if needed

    @property
    def current_state(self) -> Optional[HState]:
        """Returns the current leaf HState instance."""
        return self._current_leaf_instance

    def _get_or_create_instance(self, state_class: Type[HState], 
                                parent_instance: Optional[HState],
                                constructor_kwargs: Dict[str, Any]) -> HState:
        if state_class not in self._instance_cache:
            # print(f"HSM_DEBUG: Creating new instance of {state_class.__name__} with {constructor_kwargs}")
            self._instance_cache[state_class] = state_class(self, parent_instance, **constructor_kwargs)
        else:
            instance = self._instance_cache[state_class]
            # print(f"HSM_DEBUG: Using cached instance of {state_class.__name__}. Constructor_kwargs {constructor_kwargs} ignored.")
            # Optionally, re-parent if necessary, though this can be complex.
            if instance._parent != parent_instance: # Naive reparenting check
                # print(f"HSM_DEBUG: Warning - Parent of cached {state_class.__name__} is being changed.")
                instance._parent = parent_instance
        return self._instance_cache[state_class]

    def _build_path_to_root_for_instance(self, leaf_instance: HState) -> List[HState]:
        path = []
        curr = leaf_instance
        while curr:
            path.insert(0, curr)
            curr = curr.parent
        return path

    def start(self, root_state_class: Type[HState], 
              constructor_kwargs_map: Optional[Dict[Type[HState], Dict[str, Any]]] = None,
              enter_kwargs_map: Optional[Dict[Type[HState], Dict[str, Any]]] = None):
        if self._current_leaf_instance:
            raise RuntimeError("HSM has already been started.")
        if self._is_transitioning:
            raise RuntimeError("Cannot start HSM during an ongoing transition.")

        self._is_transitioning = True
        _constructor_kwargs_map = constructor_kwargs_map or {}
        _enter_kwargs_map = enter_kwargs_map or {}

        # print(f"HSM_DEBUG: Starting HSM with root {root_state_class.__name__}")
        root_constructor_kwargs = _constructor_kwargs_map.get(root_state_class, {})
        root_instance = self._get_or_create_instance(root_state_class, None, root_constructor_kwargs)
        
        root_enter_kwargs = _enter_kwargs_map.get(root_state_class, {})
        self._current_leaf_instance = root_instance._enter_state_internal(root_enter_kwargs, _constructor_kwargs_map, _enter_kwargs_map)
        self._active_states_path = self._build_path_to_root_for_instance(self._current_leaf_instance)
        
        # print(f"HSM_DEBUG: HSM started. Active path: {[s.__class__.__name__ for s in self._active_states_path]}")
        self._is_transitioning = False

    def dispatch(self, event: Any, **kwargs) -> bool:
        if self._is_transitioning:
            # print("HSM_DEBUG: Dispatch called during transition, event ignored.")
            return False # Or raise error
        if not self._current_leaf_instance:
            # print("HSM_DEBUG: Dispatch called but HSM not started or no current state.")
            return False # Or raise error

        # print(f"HSM_DEBUG: Dispatching event '{event}' to path ending in {self._current_leaf_instance.__class__.__name__}")
        # Event dispatch starts from the root of the current path and goes down to the leaf's handler, 
        # but _handle_event_internal in HState propagates from leaf up to its own handler.
        # The current model: self._current_leaf_instance._handle_event_internal will try sub-state (if any, which it won't as leaf) then self.
        # For full hierarchical dispatch (root to leaf, then leaf to root for handling):
        # We need to iterate self._active_states_path for initial dispatch if desired.
        # Current model: event goes to leaf, which then bubbles up its handling logic if sub-states don't handle.
        # This means the leaf-most state containing the active_sub_state gets first dibs via its _active_sub_state_instance.
        return self._active_states_path[0]._handle_event_internal(event, kwargs) # Dispatch to root of current path

    def transition_to(self, target_state_class: Type[HState],
                      constructor_kwargs_map: Optional[Dict[Type[HState], Dict[str, Any]]] = None,
                      enter_kwargs_map: Optional[Dict[Type[HState], Dict[str, Any]]] = None,
                      exit_kwargs_map: Optional[Dict[Type[HState], Dict[str, Any]]] = None):
        if self._is_transitioning:
            # print("HSM_DEBUG: Transition called while another is in progress. Ignoring.")
            return
        if not self._current_leaf_instance:
            raise RuntimeError("HSM not started, cannot transition.")

        self._is_transitioning = True
        _constructor_kwargs_map = constructor_kwargs_map or {}
        _enter_kwargs_map = enter_kwargs_map or {}
        _exit_kwargs_map = exit_kwargs_map or {}

        # print(f"HSM_DEBUG: Transitioning to {target_state_class.__name__} (full exit/enter model)")

        if self._current_leaf_instance:
            # Exit the entire current hierarchy from root down to leaf
            # The _exit_state_internal on the root will cascade exits.
            root_of_current_path = self._active_states_path[0]
            root_exit_kwargs = _exit_kwargs_map.get(root_of_current_path.__class__, {})
            root_of_current_path._exit_state_internal(root_exit_kwargs, _exit_kwargs_map)
        
        self._active_states_path = []
        self._current_leaf_instance = None
        # Note: Instance cache is not cleared here. States are reused if transitioned back.

        # print(f"HSM_DEBUG: Entering new path starting from {target_state_class.__name__}")
        new_root_constructor_kwargs = _constructor_kwargs_map.get(target_state_class, {})
        new_root_instance = self._get_or_create_instance(target_state_class, None, new_root_constructor_kwargs)
        
        new_root_enter_kwargs = _enter_kwargs_map.get(target_state_class, {})
        self._current_leaf_instance = new_root_instance._enter_state_internal(new_root_enter_kwargs, _constructor_kwargs_map, _enter_kwargs_map)
        self._active_states_path = self._build_path_to_root_for_instance(self._current_leaf_instance)

        # print(f"HSM_DEBUG: Transition complete. New active path: {[s.__class__.__name__ for s in self._active_states_path]}")
        self._is_transitioning = False

    def get_active_states_path_names(self) -> List[str]:
        """Helper for debugging or inspection. Returns class names of active states from root to leaf."""
        return [s.__class__.__name__ for s in self._active_states_path]

    def get_active_state_by_class(self, state_class: Type[HState]) -> Optional[HState]:
        """Returns the active state instance of the given class, if it's in the current path."""
        for state_instance in self._active_states_path:
            if isinstance(state_instance, state_class):
                return state_instance
        return None
