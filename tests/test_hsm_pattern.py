import unittest
from typing import Any, Type, Optional, Dict, List
from gamepp.patterns.hsm import HState, HStateMachine

# --- Test States ---

class EventLogger:
    def __init__(self):
        self.log: List[str] = []
        self.details: Dict[str, List[Dict[str, Any]]] = {}

    def add(self, event_type: str, state_name: str, *args, **kwargs_for_event):
        entry = f"{state_name}:{event_type}"
        self.log.append(entry)
        
        detail_to_store = {}
        if args:
            detail_to_store['args'] = args
        if kwargs_for_event:
            detail_to_store['kwargs'] = kwargs_for_event
        
        if detail_to_store:
            if entry not in self.details:
                self.details[entry] = []
            self.details[entry].append(detail_to_store)

    def clear(self):
        self.log.clear()
        self.details.clear()


class BaseTestHState(HState):
    def __init__(self, context: HStateMachine, parent: Optional[HState] = None, logger: Optional[EventLogger] = None, **kwargs):
        super().__init__(context, parent, **kwargs)
        self.logger = logger if logger is not None else getattr(context, 'hsm_logger', None)
        self.init_kwargs_received = kwargs
        if self.logger:
            self.logger.add("init", self.__class__.__name__, **self.init_kwargs_received)

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
            self.logger.add("handle", self.__class__.__name__, event_name=event, **kwargs)
        self.event_kwargs = kwargs
        self.last_event_handled = event 
        return False


class GrandChildA1State(BaseTestHState):
    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        if event == "EVENT_GC_A1":
            if self.logger: self.logger.add("handled_by", self.__class__.__name__, event_name=event, **kwargs)
            return True
        if event == "TRANSITION_TO_CHILD_B":
            if self.logger: self.logger.add("transitioning_to_ChildB", self.__class__.__name__, event_name=event, **kwargs)
            self.context.transition_to(ChildBState)
            return True
        return False


class GrandChildB1State(BaseTestHState):
    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        return False


class ChildAState(BaseTestHState):
    default_child_state_class = GrandChildA1State

    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        if event == "EVENT_CHILD_A":
            if self.logger: self.logger.add("handled_by", self.__class__.__name__, event_name=event, **kwargs)
            return True
        return False


class ChildBState(BaseTestHState):
    default_child_state_class = GrandChildB1State

    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        if event == "TRANSITION_TO_GC_A1":
            if self.logger: self.logger.add("transitioning_to_GrandChildA1State", self.__class__.__name__, event_name=event, **kwargs)
            self.context.transition_to(GrandChildA1State)
            return True
        if event == "BACK_TO_A":
            if self.logger: self.logger.add("transitioning_to_ChildA", self.__class__.__name__, event_name=event, **kwargs)
            self.context.transition_to(ChildAState)
            return True
        return False


class RootState(BaseTestHState):
    default_child_state_class = ChildAState

    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        if event == "EVENT_ROOT":
            if self.logger: self.logger.add("handled_by", self.__class__.__name__, event_name=event, **kwargs)
            return True
        if event == "TRANSITION_TO_CHILD_A_FROM_ROOT":
            if self.logger: self.logger.add("transitioning_to_ChildA", self.__class__.__name__, event_name=event, **kwargs)
            self.context.transition_to(ChildAState)
            return True
        return False


class SimpleRootState(BaseTestHState):
    def on_handle_event(self, event: Any, **kwargs) -> bool:
        super().on_handle_event(event, **kwargs)
        if event == "SIMPLE_EVENT":
            if self.logger: self.logger.add("handled_by", self.__class__.__name__, event_name=event, **kwargs)
            return True
        return False


# --- Test Cases ---

class TestHierarchicalStateMachine(unittest.TestCase):
    def setUp(self):
        self.logger = EventLogger()
        self.hsm = HStateMachine(logger=self.logger)

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

        root_init_details_list = self.logger.details.get("RootState:init")
        self.assertIsNotNone(root_init_details_list)
        self.assertEqual(len(root_init_details_list), 1)
        self.assertEqual(root_init_details_list[0]['kwargs'].get("constructor_arg"), "root_val")
        
        gc_enter_details_list = self.logger.details.get("GrandChildA1State:enter")
        self.assertIsNotNone(gc_enter_details_list)
        self.assertEqual(len(gc_enter_details_list), 1)
        self.assertEqual(gc_enter_details_list[0]['kwargs'].get("enter_arg"), "gcA1_enter")


    def test_event_handling_handled_by_leaf(self):
        self.hsm.start(RootState, constructor_kwargs_map={s: {"logger": self.logger} for s in [RootState, ChildAState, GrandChildA1State]})
        self.logger.log.clear()

        handled = self.hsm.dispatch("EVENT_GC_A1", event_arg="gc_a1_dispatch")
        self.assertTrue(handled)
        expected_log = [
            "GrandChildA1State:handle", 
            "GrandChildA1State:handled_by" 
        ]
        self.assertEqual(self.logger.log, expected_log)


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
        all_states = [RootState, ChildAState, GrandChildA1State, ChildBState, GrandChildB1State]
        self.hsm.start(RootState, constructor_kwargs_map={s: {"logger": self.logger} for s in all_states})
        self.logger.clear()

        self.hsm.dispatch("TRANSITION_TO_CHILD_B")

        self.assertIsInstance(self.hsm.current_state, GrandChildB1State)
        self.assertEqual(self.hsm.get_active_states_path_names(), ["ChildBState", "GrandChildB1State"])
        
        log = self.logger.log
        self.assertIn("GrandChildA1State:handle", log)
        self.assertIn("GrandChildA1State:transitioning_to_ChildB", log)
        self.assertIn("RootState:exit", log)
        self.assertIn("ChildAState:exit", log)
        self.assertIn("GrandChildA1State:exit", log)
        self.assertIn("ChildBState:enter", log)
        self.assertIn("GrandChildB1State:enter", log)
        
        idx_gca1_exit = log.index("GrandChildA1State:exit")
        idx_childb_enter = log.index("ChildBState:enter")
        self.assertLess(idx_gca1_exit, idx_childb_enter, "Exit from old branch must precede entry into new branch")


    def test_transition_to_deeper_state_in_new_branch(self):
        all_states = [RootState, ChildAState, GrandChildA1State, ChildBState, GrandChildB1State]
        self.hsm.start(RootState, constructor_kwargs_map={s: {"logger": self.logger} for s in all_states})
        self.logger.clear()

        self.hsm.transition_to(GrandChildB1State,
                               enter_kwargs_map={GrandChildB1State: {"reason": "direct_transition_to_leaf"}})

        self.assertIsInstance(self.hsm.current_state, GrandChildB1State)
        self.assertEqual(self.hsm.get_active_states_path_names(), ["GrandChildB1State"])

        log = self.logger.log
        self.assertIn("RootState:exit", log)
        self.assertIn("ChildAState:exit", log)
        self.assertIn("GrandChildA1State:exit", log)
        self.assertIn("GrandChildB1State:enter", log)
        
        gcb1_enter_details_list = self.logger.details.get("GrandChildB1State:enter")
        self.assertIsNotNone(gcb1_enter_details_list)
        self.assertTrue(any(d['kwargs'].get("reason") == "direct_transition_to_leaf" for d in gcb1_enter_details_list))


    def test_instance_caching_and_reentry(self):
        all_states = [RootState, ChildAState, GrandChildA1State, ChildBState, GrandChildB1State]
        constructor_map = {s: {"logger": self.logger, "id": s.__name__ + "_instance"} for s in all_states}

        self.hsm.start(RootState, constructor_kwargs_map=constructor_map)
        self.assertIsInstance(self.hsm.current_state, GrandChildA1State)
        gca1_first_instance = self.hsm.current_state

        self.logger.clear()

        self.hsm.dispatch("TRANSITION_TO_CHILD_B")
        self.assertIsInstance(self.hsm.current_state, GrandChildB1State)
        gcb1_first_instance = self.hsm.current_state
        childb_first_instance = self.hsm.get_active_state_by_class(ChildBState)

        log1 = self.logger.log[:]
        self.assertIn("GrandChildA1State:transitioning_to_ChildB", log1)
        self.assertIn("RootState:exit", log1)
        self.assertIn("ChildBState:enter", log1)
        self.assertIn("GrandChildB1State:enter", log1)
        
        child_b_init_logged = any(
            entry == "ChildBState:init" and 
            self.logger.details.get(entry) and 
            any(detail_item['kwargs'].get('id') == "ChildBState_instance" for detail_item in self.logger.details[entry])
            for entry in log1
        )
        self.assertTrue(child_b_init_logged, "ChildBState:init with correct id should be logged on first transition")

        self.logger.clear()

        self.hsm.dispatch("BACK_TO_A")
        self.assertIsInstance(self.hsm.current_state, GrandChildA1State)
        self.assertEqual(self.hsm.get_active_states_path_names(), ["ChildAState", "GrandChildA1State"])
        
        self.assertIs(self.hsm.current_state, gca1_first_instance, "GrandChildA1State instance should be cached")

        log2 = self.logger.log[:]
        self.assertIn("ChildBState:transitioning_to_ChildA", log2)
        self.assertIn("ChildBState:exit", log2)
        self.assertIn("GrandChildB1State:exit", log2)
        self.assertNotIn("ChildAState:init", log2, "ChildAState should be cached")
        self.assertIn("ChildAState:enter", log2)
        self.assertNotIn("GrandChildA1State:init", log2, "GCA1 should be cached")
        self.assertIn("GrandChildA1State:enter", log2)

        self.logger.clear()

        self.hsm.dispatch("TRANSITION_TO_CHILD_B")
        self.assertIsInstance(self.hsm.current_state, GrandChildB1State)
        
        self.assertIs(self.hsm.current_state, gcb1_first_instance, "GCB1 instance should be cached")
        self.assertIs(self.hsm.get_active_state_by_class(ChildBState), childb_first_instance, "ChildB instance should be cached")

        log3 = self.logger.log[:]
        self.assertNotIn("ChildBState:init", log3)
        self.assertIn("ChildBState:enter", log3)
        self.assertNotIn("GrandChildB1State:init", log3)
        self.assertIn("GrandChildB1State:enter", log3)


    def test_runtime_errors(self):
        self.hsm.start(SimpleRootState, constructor_kwargs_map={SimpleRootState: {"logger": self.logger}})
        with self.assertRaises(RuntimeError):
            self.hsm.start(SimpleRootState)

        new_hsm = HStateMachine()
        with self.assertRaises(RuntimeError):
            new_hsm.transition_to(SimpleRootState)
        
        self.assertFalse(new_hsm.dispatch("ANY_EVENT"))


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

