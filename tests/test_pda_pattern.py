import unittest
from gamepp.patterns.pda import PushdownAutomata, PDAState
from typing import Any, List


class MockState(PDAState):
    def __init__(self, name: str):
        self.name = name
        self.entered = False
        self.exited = False
        self.inputs_handled: List[Any] = []
        self.pda_on_enter: PushdownAutomata | None = None
        self.pda_on_exit: PushdownAutomata | None = None
        self.pda_on_handle_input: PushdownAutomata | None = None

    def enter(self, pda: PushdownAutomata) -> None:
        self.entered = True
        self.pda_on_enter = pda

    def exit(self, pda: PushdownAutomata) -> None:
        self.exited = True
        self.pda_on_exit = pda

    def handle_input(self, pda: PushdownAutomata, input_data: Any) -> None:
        self.inputs_handled.append(input_data)
        self.pda_on_handle_input = pda
        if input_data == f"pop_{self.name}":
            pda.pop_state()
        elif isinstance(input_data, dict) and input_data.get("action") == "push":
            next_state_name = input_data.get("state_name", "NextState")
            pda.push_state(MockState(next_state_name))

    def __repr__(self):
        return f"<MockState {self.name}>"


class TestPushdownAutomata(unittest.TestCase):
    def test_initialization_empty(self):
        pda = PushdownAutomata()
        self.assertIsNone(pda.current_state)
        self.assertEqual(pda.stack_depth, 0)

    def test_initialization_with_state(self):
        initial_state = MockState("Initial")
        pda = PushdownAutomata(initial_state)
        self.assertIs(pda.current_state, initial_state)
        self.assertTrue(initial_state.entered)
        self.assertFalse(initial_state.exited)
        self.assertEqual(pda.stack_depth, 1)
        self.assertIs(initial_state.pda_on_enter, pda)

    def test_push_state(self):
        pda = PushdownAutomata()
        state1 = MockState("State1")

        pda.push_state(state1)
        self.assertIs(pda.current_state, state1)
        self.assertTrue(state1.entered)
        self.assertFalse(state1.exited)
        self.assertEqual(pda.stack_depth, 1)
        self.assertIs(state1.pda_on_enter, pda)

        state2 = MockState("State2")
        pda.push_state(state2)
        self.assertIs(pda.current_state, state2)
        self.assertTrue(state2.entered)
        self.assertFalse(state2.exited)
        self.assertEqual(pda.stack_depth, 2)
        self.assertIs(state2.pda_on_enter, pda)

        self.assertFalse(state1.exited)

    def test_pop_state(self):
        state1 = MockState("State1")
        state2 = MockState("State2")
        pda = PushdownAutomata(state1)
        pda.push_state(state2)

        self.assertEqual(pda.stack_depth, 2)

        popped_state = pda.pop_state()
        self.assertIs(popped_state, state2)
        self.assertTrue(state2.exited)
        self.assertIs(state2.pda_on_exit, pda)
        self.assertIs(pda.current_state, state1)
        self.assertEqual(pda.stack_depth, 1)

        self.assertFalse(state1.exited)
        self.assertTrue(state1.entered)

        popped_state = pda.pop_state()
        self.assertIs(popped_state, state1)
        self.assertTrue(state1.exited)
        self.assertIs(state1.pda_on_exit, pda)
        self.assertIsNone(pda.current_state)
        self.assertEqual(pda.stack_depth, 0)

    def test_pop_empty_stack(self):
        pda = PushdownAutomata()
        popped = pda.pop_state()
        self.assertIsNone(popped)
        self.assertEqual(pda.stack_depth, 0)

    def test_handle_input_current_state(self):
        state1 = MockState("State1")
        pda = PushdownAutomata(state1)

        pda.handle_input("test_input_1")
        self.assertEqual(state1.inputs_handled, ["test_input_1"])
        self.assertIs(state1.pda_on_handle_input, pda)

        state2 = MockState("State2")
        pda.push_state(state2)
        pda.handle_input("test_input_2")
        self.assertEqual(state1.inputs_handled, ["test_input_1"])
        self.assertEqual(state2.inputs_handled, ["test_input_2"])
        self.assertIs(state2.pda_on_handle_input, pda)

    def test_handle_input_empty_stack(self):
        pda = PushdownAutomata()
        try:
            pda.handle_input("some_input")
        except Exception as e:
            self.fail(f"handle_input on empty stack raised an exception: {e}")

    def test_state_popping_itself(self):
        state_a = MockState("A")
        pda = PushdownAutomata(state_a)

        self.assertIs(pda.current_state, state_a)
        pda.handle_input("pop_A")

        self.assertIsNone(pda.current_state)
        self.assertTrue(state_a.exited)
        self.assertEqual(state_a.inputs_handled, ["pop_A"])
        self.assertEqual(pda.stack_depth, 0)

    def test_state_pushing_new_state(self):
        state_a = MockState("A")
        pda = PushdownAutomata(state_a)

        self.assertIs(pda.current_state, state_a)
        pda.handle_input({"action": "push", "state_name": "B"})

        self.assertEqual(pda.stack_depth, 2)
        self.assertIsInstance(pda.current_state, MockState)
        self.assertEqual(pda.current_state.name, "B")
        self.assertTrue(pda.current_state.entered)
        self.assertFalse(state_a.exited)
        self.assertEqual(
            state_a.inputs_handled, [{"action": "push", "state_name": "B"}]
        )

        state_b = pda.current_state
        self.assertIs(state_b.pda_on_enter, pda)

    def test_complex_interaction_push_pop(self):
        state_a = MockState("A")
        pda = PushdownAutomata(state_a)
        self.assertEqual(pda.current_state.name, "A")
        self.assertEqual(pda.stack_depth, 1)

        pda.handle_input({"action": "push", "state_name": "B"})
        self.assertEqual(pda.current_state.name, "B")
        self.assertEqual(pda.stack_depth, 2)
        state_b = pda.current_state
        self.assertTrue(state_b.entered)
        self.assertFalse(state_a.exited)

        pda.handle_input({"action": "push", "state_name": "C"})
        self.assertEqual(pda.current_state.name, "C")
        self.assertEqual(pda.stack_depth, 3)
        state_c = pda.current_state
        self.assertTrue(state_c.entered)
        self.assertFalse(state_b.exited)

        pda.handle_input("pop_C")
        self.assertEqual(pda.current_state.name, "B")
        self.assertEqual(pda.stack_depth, 2)
        self.assertTrue(state_c.exited)
        self.assertFalse(state_b.exited)

        pda.handle_input("pop_B")
        self.assertEqual(pda.current_state.name, "A")
        self.assertEqual(pda.stack_depth, 1)
        self.assertTrue(state_b.exited)
        self.assertFalse(state_a.exited)

        pda.handle_input("pop_A")
        self.assertIsNone(pda.current_state)
        self.assertEqual(pda.stack_depth, 0)
        self.assertTrue(state_a.exited)


if __name__ == "__main__":
    unittest.main()
