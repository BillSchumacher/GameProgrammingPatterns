"""
Unit tests for the Bytecode pattern.
"""
import unittest
from gpp.patterns.bytecode import Instruction, VirtualMachine

class TestBytecodePattern(unittest.TestCase):
    """Tests the Bytecode pattern implementation."""

    def setUp(self):
        """Set up for test methods."""
        self.vm = VirtualMachine()

    def test_literal_and_stack(self):
        """Test pushing literals onto the stack."""
        bytecode = [Instruction.LITERAL, 10]
        self.vm.interpret(bytecode)
        self.assertEqual(self.vm.stack, [10])

    def test_add_operation(self):
        """Test the ADD instruction."""
        bytecode = [
            Instruction.LITERAL, 5,
            Instruction.LITERAL, 3,
            Instruction.ADD
        ]
        result = self.vm.interpret(bytecode)
        self.assertEqual(result, 8)
        self.assertEqual(self.vm.stack, [8])

    def test_subtract_operation(self):
        """Test the SUBTRACT instruction."""
        bytecode = [
            Instruction.LITERAL, 10,
            Instruction.LITERAL, 4,
            Instruction.SUBTRACT
        ]
        result = self.vm.interpret(bytecode)
        self.assertEqual(result, 6)
        self.assertEqual(self.vm.stack, [6])

    def test_multiply_operation(self):
        """Test the MULTIPLY instruction."""
        bytecode = [
            Instruction.LITERAL, 7,
            Instruction.LITERAL, 3,
            Instruction.MULTIPLY
        ]
        result = self.vm.interpret(bytecode)
        self.assertEqual(result, 21)
        self.assertEqual(self.vm.stack, [21])

    def test_divide_operation(self):
        """Test the DIVIDE instruction."""
        bytecode = [
            Instruction.LITERAL, 20,
            Instruction.LITERAL, 4,
            Instruction.DIVIDE
        ]
        result = self.vm.interpret(bytecode)
        self.assertEqual(result, 5.0)
        self.assertEqual(self.vm.stack, [5.0])

    def test_complex_expression(self):
        """Test a more complex sequence of instructions: (10 + 5) * 2 / 3 - 1"""
        bytecode = [
            Instruction.LITERAL, 10,
            Instruction.LITERAL, 5,
            Instruction.ADD,        # Stack: [15]
            Instruction.LITERAL, 2,
            Instruction.MULTIPLY,   # Stack: [30]
            Instruction.LITERAL, 3,
            Instruction.DIVIDE,     # Stack: [10.0]
            Instruction.LITERAL, 1,
            Instruction.SUBTRACT    # Stack: [9.0]
        ]
        result = self.vm.interpret(bytecode)
        self.assertEqual(result, 9.0)
        self.assertEqual(self.vm.stack, [9.0])

    def test_stack_underflow_add(self):
        """Test stack underflow for ADD."""
        bytecode = [Instruction.LITERAL, 1, Instruction.ADD]
        with self.assertRaisesRegex(ValueError, "Stack underflow during ADD operation."):
            self.vm.interpret(bytecode)

    def test_stack_underflow_subtract(self):
        """Test stack underflow for SUBTRACT."""
        bytecode = [Instruction.SUBTRACT]
        with self.assertRaisesRegex(ValueError, "Stack underflow during SUBTRACT operation."):
            self.vm.interpret(bytecode)

    def test_stack_underflow_multiply(self):
        """Test stack underflow for MULTIPLY."""
        bytecode = [Instruction.LITERAL, 5, Instruction.MULTIPLY]
        with self.assertRaisesRegex(ValueError, "Stack underflow during MULTIPLY operation."):
            self.vm.interpret(bytecode)

    def test_stack_underflow_divide(self):
        """Test stack underflow for DIVIDE."""
        bytecode = [Instruction.DIVIDE]
        with self.assertRaisesRegex(ValueError, "Stack underflow during DIVIDE operation."):
            self.vm.interpret(bytecode)

    def test_division_by_zero(self):
        """Test division by zero."""
        bytecode = [
            Instruction.LITERAL, 10,
            Instruction.LITERAL, 0,
            Instruction.DIVIDE
        ]
        with self.assertRaises(ZeroDivisionError):
            self.vm.interpret(bytecode)

    def test_unknown_instruction(self):
        """Test handling of an unknown instruction."""
        bytecode = [Instruction.LITERAL, 5, "UNKNOWN_INST", Instruction.ADD]
        with self.assertRaisesRegex(ValueError, "Unknown instruction: UNKNOWN_INST"):
            self.vm.interpret(bytecode)
    
    def test_interpret_empty_bytecode(self):
        """Test interpreting an empty bytecode sequence."""
        result = self.vm.interpret([])
        self.assertIsNone(result)
        self.assertEqual(self.vm.stack, [])

    def test_interpret_multiple_results_on_stack(self):
        """Test scenario where multiple results are left on stack (if allowed)."""
        bytecode = [
            Instruction.LITERAL, 10,
            Instruction.LITERAL, 20
        ]
        result = self.vm.interpret(bytecode)
        # Assuming the VM returns the entire stack if more than one item is left
        self.assertEqual(result, [10, 20]) 
        self.assertEqual(self.vm.stack, [10, 20])

if __name__ == '__main__':
    unittest.main()
