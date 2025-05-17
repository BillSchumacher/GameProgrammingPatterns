import unittest
from gamepp.patterns.csm import CSM, StateMachineInterface
from typing import Any


class MockStateMachine(StateMachineInterface):
    def __init__(self):
        self.input_received = None
        self.input_count = 0

    def handle_input(self, input_data: Any) -> None:
        self.input_received = input_data
        self.input_count += 1


class TestCSM(unittest.TestCase):
    def test_add_and_handle_input(self):
        csm = CSM()
        sm1 = MockStateMachine()
        sm2 = MockStateMachine()

        csm.add_state_machine(sm1)
        csm.add_state_machine(sm2)

        self.assertIn(sm1, csm.state_machines)
        self.assertIn(sm2, csm.state_machines)

        test_input = "test_event"
        csm.handle_input(test_input)

        self.assertEqual(sm1.input_received, test_input)
        self.assertEqual(sm1.input_count, 1)
        self.assertEqual(sm2.input_received, test_input)
        self.assertEqual(sm2.input_count, 1)

    def test_remove_state_machine(self):
        csm = CSM()
        sm1 = MockStateMachine()
        csm.add_state_machine(sm1)
        self.assertIn(sm1, csm.state_machines)

        csm.remove_state_machine(sm1)
        self.assertNotIn(sm1, csm.state_machines)

        # Test removing a non-existent state machine (should not raise error)
        sm_non_existent = MockStateMachine()
        csm.remove_state_machine(sm_non_existent)

    def test_handle_input_no_state_machines(self):
        csm = CSM()
        # Should not raise an error
        csm.handle_input("some_input")

    def test_add_duplicate_state_machine(self):
        csm = CSM()
        sm1 = MockStateMachine()
        csm.add_state_machine(sm1)
        csm.add_state_machine(sm1)  # Adding the same instance again
        self.assertEqual(len(csm.state_machines), 1)

    def test_add_invalid_state_machine(self):
        csm = CSM()

        class InvalidSM:
            pass

        invalid_sm = InvalidSM()
        with self.assertRaises(ValueError):
            csm.add_state_machine(invalid_sm)  # type: ignore


if __name__ == "__main__":
    unittest.main()
