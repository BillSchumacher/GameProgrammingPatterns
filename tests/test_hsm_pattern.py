import unittest
from typing import Any, Type, Optional, Dict, List
from gpp.patterns.hsm import HState, HStateMachine

# --- Test States ---

class EventLogger:
    def __init__(self):
        self.log: List[str] = []
        self.details: Dict[str, List[Any]] = {} # To store kwargs

    def add(self, event_type: str, state_name: str, *args, **kwargs):
        self.log.append(f"{state_name}:{event_type}")
        if args or kwargs:
            entry_details = []
            if args:
                entry_details.extend(list(args))
            if kwargs:
                entry_details.append(kwargs)
            
            key = f"{state_name}:{event_type}"
            if key not in self.details:
                self.details[key] = []
            self.details[key].append(entry_details[0] if len(entry_details) == 1 else entry_details)

    def clear(self):
        self.log.clear()
        self.details.clear()


class BaseTestHState(HState):
    def __init__(self, context: HStateMachine, parent: Optional[HState] = None, logger: Optional[EventLogger] = None, **kwargs):
        super().__init__(context, parent)
        self.logger = logger
        self.init_kwargs = kwargs
        if self.logger:
            self.logger.add("init", self.__class__.__name__, **kwargs)

    def on_enter(self, **kwargs) -> None:
        if self.logger:
            self.logger.add("enter", self.__class__.__name__, **kwargs)
        self.enter_kwargs = kwargs

    def on_exit(self, **kwargs) -> None:
        if self.logger:
            self.logger.add("exit", self.__class__.__name__, **kwargs)
        self.exit_kwargs = kwargs

    def on_handle_event(self, event: Any, **kwargs) -> bool:
        if self.logger:
            self.logger.add("handle", self.__class__.__name__, event_arg=kwargs.get("event_arg"), event_data=event)
        self.event_kwargs = kwargs
        self.last_event_handled = event
        return False # Default: event not handled, propagates up

class GrandChildA1State(BaseTestHState):
    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        if event == "EVENT_GC_A1":
            if self.logger: self.logger.add("handled_by", self.__class__.__name__)
            return True
        if event == "TRANSITION_TO_CHILD_B":
            self.context.transition_to(ChildBState)
            if self.logger: self.logger.add("handled_by", self.__class__.__name__)
            return True
        return False

class GrandChildB1State(BaseTestHState):
    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        return False # Does not handle any events itself by default

class ChildAState(BaseTestHState):
    def get_initial_sub_state_class(self) -> Optional[Type[HState]]:
        return GrandChildA1State

    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        if event == "EVENT_CHILD_A":
            if self.logger: self.logger.add("handled_by", self.__class__.__name__)
            return True
        return False

class ChildBState(BaseTestHState):
    default_child_state_class = GrandChildB1State # Make GCB1 default child

    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        if event == "TRANSITION_TO_GC_A1":
            self.context.transition_to(GrandChildA1State)
            if self.logger: self.logger.add("handled_by", self.__class__.__name__)
            return True
        return False

class RootState(BaseTestHState):
    def get_initial_sub_state_class(self) -> Optional[Type[HState]]:
        return ChildAState # Default to ChildA

    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        if event == "EVENT_ROOT":
            if self.logger: self.logger.add("handled_by", self.__class__.__name__)
            return True
        if event == "TRANSITION_TO_CHILD_A_FROM_ROOT":
            self.context.transition_to(ChildAState)
            if self.logger: self.logger.add("handled_by", self.__class__.__name__)
            return True
        return False

class SimpleRootState(BaseTestHState): # No sub-states
    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        if event == "SIMPLE_EVENT":
            if self.logger: self.logger.add("handled_by", self.__class__.__name__)
            return True
        return False

# --- Test Cases ---

class TestHierarchicalStateMachine(unittest.TestCase):
    def setUp(self):
        self.logger = EventLogger()
        self.hsm = HStateMachine()

    def test_initialization_and_start(self):
        constructor_args = {
            RootState: {"constructor_arg": "root_val", "logger": self.logger},
            ChildAState: {"constructor_arg": "childA_val", "logger": self.logger},
            GrandChildA1State: {"constructor_arg": "gcA1_val", "logger": self.logger}
        }
        enter_args = {
            RootState: {"enter_arg": "root_enter"},
            ChildAState: {"enter_arg": "childA_enter"},
            GrandChildA1State: {"enter_arg": "gcA1_enter"}
        }
        self.hsm.start(RootState, constructor_kwargs_map=constructor_args, enter_kwargs_map=enter_args)

        self.assertIsInstance(self.hsm.current_state, GrandChildA1State)
        self.assertEqual(self.hsm.get_active_states_path_names(), ["RootState", "ChildAState", "GrandChildA1State"])

        expected_log = [
            "RootState:init",
            "RootState:enter",
            "ChildAState:init",
            "ChildAState:enter",
            "GrandChildA1State:init",
            "GrandChildA1State:enter"
        ]
        self.assertEqual(self.logger.log, expected_log)

        # Check kwargs
        root_init_details = self.logger.details["RootState:init"][0]
        self.assertEqual(root_init_details.get("constructor_arg"), "root_val")
        
        gc_enter_details = self.logger.details["GrandChildA1State:enter"][0]
        self.assertEqual(gc_enter_details.get("enter_arg"), "gcA1_enter")

        # Check parent linking
        gc_state = self.hsm.current_state
        child_state = gc_state.parent
        root_state = child_state.parent
        self.assertIsInstance(child_state, ChildAState)
        self.assertIsInstance(root_state, RootState)
        self.assertIsNone(root_state.parent)

        # Check active sub-state linking
        self.assertIs(root_state.active_sub_state_instance, child_state)
        self.assertIs(child_state.active_sub_state_instance, gc_state)
        self.assertIsNone(gc_state.active_sub_state_instance)


    def test_event_handling_handled_by_leaf(self):
        self.hsm.start(RootState, constructor_kwargs_map={s: {"logger": self.logger} for s in [RootState, ChildAState, GrandChildA1State]})
        self.logger.log.clear() # Clear init/enter logs

        handled = self.hsm.dispatch("EVENT_GC_A1", event_arg="gc_a1_dispatch")
        self.assertTrue(handled)
        expected_log = [
            "GrandChildA1State:handle", 
            "GrandChildA1State:handled_by"
        ]
        self.assertEqual(self.logger.log, expected_log)
        
        gc_state = self.hsm.get_active_state_by_class(GrandChildA1State)
        self.assertIsNotNone(gc_state)
        self.assertEqual(gc_state.last_event_handled, "EVENT_GC_A1")
        self.assertEqual(gc_state.event_kwargs.get("event_arg"), "gc_a1_dispatch")


    def test_event_handling_handled_by_parent(self):
        self.hsm.start(RootState, constructor_kwargs_map={s: {"logger": self.logger} for s in [RootState, ChildAState, GrandChildA1State]})
        self.logger.log.clear()

        handled = self.hsm.dispatch("EVENT_CHILD_A", event_arg="child_a_dispatch")
        self.assertTrue(handled)
        
        expected_log_corrected = [
            "GrandChildA1State:handle", 
            "ChildAState:handle", 
            "ChildAState:handled_by"
        ]
        self.assertEqual(self.logger.log, expected_log_corrected)
        
        child_a_state = self.hsm.get_active_state_by_class(ChildAState)
        self.assertIsNotNone(child_a_state)
        self.assertEqual(child_a_state.last_event_handled, "EVENT_CHILD_A")
        self.assertEqual(child_a_state.event_kwargs.get("event_arg"), "child_a_dispatch")


    def test_event_handling_handled_by_root(self):
        self.hsm.start(RootState, constructor_kwargs_map={s: {"logger": self.logger} for s in [RootState, ChildAState, GrandChildA1State]})
        self.logger.log.clear()

        handled = self.hsm.dispatch("EVENT_ROOT", event_arg="root_dispatch")
        self.assertTrue(handled)
        expected_log = [
            "GrandChildA1State:handle",
            "ChildAState:handle",
            "RootState:handle", 
            "RootState:handled_by"
        ]
        self.assertEqual(self.logger.log, expected_log)
        
        root_state = self.hsm.get_active_state_by_class(RootState)
        self.assertIsNotNone(root_state)
        self.assertEqual(root_state.last_event_handled, "EVENT_ROOT")
        self.assertEqual(root_state.event_kwargs.get("event_arg"), "root_dispatch")

    def test_event_not_handled(self):
        self.hsm.start(RootState, constructor_kwargs_map={s: {"logger": self.logger} for s in [RootState, ChildAState, GrandChildA1State]})
        self.logger.log.clear()

        handled = self.hsm.dispatch("UNKNOWN_EVENT")
        self.assertFalse(handled)
        expected_log = [
            "GrandChildA1State:handle",
            "ChildAState:handle",
            "RootState:handle",
        ]
        self.assertEqual(self.logger.log, expected_log)

    def test_transition_from_leaf_to_sibling_branch(self):
        self.hsm.start(RootState, constructor_kwargs_map={s: {"logger": self.logger} for s in [RootState, ChildAState, GrandChildA1State, ChildBState]})
        self.logger.log.clear()
        self.logger.details.clear()

        self.hsm.dispatch("TRANSITION_TO_CHILD_B")

        self.assertIsInstance(self.hsm.current_state, ChildBState)
        self.assertEqual(self.hsm.get_active_states_path_names(), ["ChildBState", "GrandChildB1State"])

        expected_log_after_dispatch_transition = [
            "RootState:handle",
            "ChildAState:handle",
            "GrandChildA1State:handle",
            "GrandChildA1State:handled_by",
            "GrandChildA1State:exit",
            "ChildAState:exit",
            "RootState:exit",
            "ChildBState:init",
            "ChildBState:enter",
            "GrandChildB1State:init",
            "GrandChildB1State:enter"
        ]
        self.assertEqual(self.logger.log, expected_log_after_dispatch_transition)

        self.assertEqual(self.logger.details.get("GrandChildA1State:exit", [{}])[0].get("exit_arg"), None)
        self.assertEqual(self.logger.details.get("ChildAState:exit", [{}])[0].get("exit_arg"), None)
        self.assertEqual(self.logger.details.get("RootState:exit", [{}])[0].get("exit_arg"), None)
        self.assertEqual(self.logger.details.get("ChildBState:enter", [{}])[0].get("enter_arg"), None)
        self.assertEqual(self.logger.details.get("ChildBState:init", [{}])[0].get("constructor_arg"), None)

    def test_transition_to_deeper_state_in_new_branch(self):
        constructor_map_for_start = {
            s: {"logger": self.logger, "id": s.__name__} 
            for s in [RootState, ChildAState, GrandChildA1State]
        }
        constructor_map_for_b_branch = {
            ChildBState: {"logger": self.logger, "id": "ChildB_transition"},
            GrandChildB1State: {"logger": self.logger, "id": "GCB1_transition"}
        }
        enter_map_for_b_branch = {
            ChildBState: {"enter_arg": "ChildB_enter_deep"},
            GrandChildB1State: {"enter_arg": "GCB1_enter_deep"}
        }
        exit_map_for_old_branch = {
            GrandChildA1State: {"exit_arg": "GCA1_exit_deep"},
            ChildAState: {"exit_arg": "ChildA_exit_deep"},
            RootState: {"exit_arg": "Root_exit_deep"}
        }

        self.hsm.start(RootState, constructor_kwargs_map=constructor_map_for_start)
        self.logger.log.clear()
        self.logger.details.clear()

        self.hsm.transition_to(
            ChildBState,
            constructor_kwargs_map=constructor_map_for_b_branch,
            enter_kwargs_map=enter_map_for_b_branch,
            exit_kwargs_map=exit_map_for_old_branch
        )

        self.assertIsInstance(self.hsm.current_state, ChildBState)
        self.assertEqual(self.hsm.get_active_states_path_names(), ["ChildBState", "GrandChildB1State"])

        expected_log = [
            "GrandChildA1State:exit",
            "ChildAState:exit",
            "RootState:exit",
            "ChildBState:init",
            "ChildBState:enter",
            "GrandChildB1State:init",
            "GrandChildB1State:enter"
        ]
        self.assertEqual(self.logger.log, expected_log)

        self.assertEqual(self.logger.details["GrandChildA1State:exit"][0].get("exit_arg"), "GCA1_exit_deep")
        self.assertEqual(self.logger.details["ChildAState:exit"][0].get("exit_arg"), "ChildA_exit_deep")
        self.assertEqual(self.logger.details["RootState:exit"][0].get("exit_arg"), "Root_exit_deep")

        self.assertEqual(self.logger.details["ChildBState:init"][0].get("id"), "ChildB_transition")
        self.assertEqual(self.logger.details["ChildBState:enter"][0].get("enter_arg"), "ChildB_enter_deep")
        
        self.assertEqual(self.logger.details["GrandChildB1State:init"][0].get("id"), "GCB1_transition")
        self.assertEqual(self.logger.details["GrandChildB1State:enter"][0].get("enter_arg"), "GCB1_enter_deep")

    def test_instance_caching_and_reentry(self):
        all_states_construct = {
            s: {"logger": self.logger, "id": s.__name__} 
            for s in [RootState, ChildAState, GrandChildA1State, ChildBState, GrandChildB1State]
        }
        start_enter_map = {
            RootState: {"enter_id": "Root_start"},
            ChildAState: {"enter_id": "ChildA_start"},
            GrandChildA1State: {"enter_id": "GCA1_start"}
        }

        self.hsm.start(RootState, constructor_kwargs_map=all_states_construct, enter_kwargs_map=start_enter_map)
        
        gca1_initial_instance = self.hsm.get_active_state_by_class(GrandChildA1State)

        self.logger.log.clear()
        self.logger.details.clear()

        self.hsm.dispatch("TRANSITION_TO_CHILD_B")
        
        self.assertIsInstance(self.hsm.current_state, ChildBState)
        path_after_to_b = self.hsm.get_active_states_path_names()
        self.assertEqual(path_after_to_b, ["ChildBState", "GrandChildB1State"])

        expected_log_to_b = [
            "RootState:handle", "ChildAState:handle", "GrandChildA1State:handle", "GrandChildA1State:handled_by",
            "GrandChildA1State:exit", "ChildAState:exit", "RootState:exit",
            "ChildBState:enter",
            "GrandChildB1State:enter"
        ]
        self.assertEqual(self.logger.log, expected_log_to_b)
        
        self.assertIn("ChildBState:enter", self.logger.details)
        self.assertEqual(self.logger.details.get("ChildBState:enter", [{}])[0].get("enter_id"), None)

        self.assertIn("GrandChildB1State:enter", self.logger.details)
        self.assertEqual(self.logger.details.get("GrandChildB1State:enter", [{}])[0].get("enter_id"), None)

        self.logger.log.clear()
        self.logger.details.clear()

        self.hsm.dispatch("TRANSITION_TO_GC_A1")

        self.assertIsInstance(self.hsm.current_state, GrandChildA1State)
        path_back_to_gc_a1 = self.hsm.get_active_states_path_names()
        self.assertEqual(path_back_to_gc_a1, ["GrandChildA1State"])

        expected_log_back_to_gc_a1 = [
            "GrandChildB1State:handle",
            "ChildBState:handle",
            "ChildBState:handled_by",
            "GrandChildB1State:exit",
            "ChildBState:exit",
            "GrandChildA1State:enter"
        ]
        self.assertEqual(self.logger.log, expected_log_back_to_gc_a1)
        self.assertNotIn("GrandChildA1State:init", self.logger.details)
        self.assertEqual(self.logger.details.get("GrandChildA1State:enter", [{}])[0].get("enter_id"), None)
        
        current_gca1_instance = self.hsm.current_state
        self.assertIs(gca1_initial_instance, current_gca1_instance, "GrandChildA1State instance should be reused")

    def test_runtime_errors(self):
        with self.assertRaisesRegex(RuntimeError, "HSM has already been started."):
            self.hsm.start(SimpleRootState, constructor_kwargs_map={SimpleRootState: {"logger": self.logger}})
            self.hsm.start(SimpleRootState) 

        self.setUp() 
        with self.assertRaisesRegex(RuntimeError, "HSM not started, cannot transition."):
            self.hsm.transition_to(SimpleRootState)

        self.assertFalse(self.hsm.dispatch("ANY_EVENT"))


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

