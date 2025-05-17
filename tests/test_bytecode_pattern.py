"""
Unit tests for the Bytecode pattern.
"""

import unittest
from gamepp.patterns.bytecode import (
    Instruction,
    VirtualMachine,
    Lexer,
    Parser,
    TokenType,
    Token,
)


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
        bytecode = [Instruction.LITERAL, 5, Instruction.LITERAL, 3, Instruction.ADD]
        result = self.vm.interpret(bytecode)
        self.assertEqual(result, 8)
        self.assertEqual(self.vm.stack, [8])

    def test_subtract_operation(self):
        """Test the SUBTRACT instruction."""
        bytecode = [
            Instruction.LITERAL,
            10,
            Instruction.LITERAL,
            4,
            Instruction.SUBTRACT,
        ]
        result = self.vm.interpret(bytecode)
        self.assertEqual(result, 6)
        self.assertEqual(self.vm.stack, [6])

    def test_multiply_operation(self):
        """Test the MULTIPLY instruction."""
        bytecode = [
            Instruction.LITERAL,
            7,
            Instruction.LITERAL,
            3,
            Instruction.MULTIPLY,
        ]
        result = self.vm.interpret(bytecode)
        self.assertEqual(result, 21)
        self.assertEqual(self.vm.stack, [21])

    def test_divide_operation(self):
        """Test the DIVIDE instruction."""
        bytecode = [Instruction.LITERAL, 20, Instruction.LITERAL, 4, Instruction.DIVIDE]
        result = self.vm.interpret(bytecode)
        self.assertEqual(result, 5.0)
        self.assertEqual(self.vm.stack, [5.0])

    def test_complex_expression(self):
        """Test a more complex sequence of instructions: (10 + 5) * 2 / 3 - 1"""
        bytecode = [
            Instruction.LITERAL,
            10,
            Instruction.LITERAL,
            5,
            Instruction.ADD,  # Stack: [15]
            Instruction.LITERAL,
            2,
            Instruction.MULTIPLY,  # Stack: [30]
            Instruction.LITERAL,
            3,
            Instruction.DIVIDE,  # Stack: [10.0]
            Instruction.LITERAL,
            1,
            Instruction.SUBTRACT,  # Stack: [9.0]
        ]
        result = self.vm.interpret(bytecode)
        self.assertEqual(result, 9.0)
        self.assertEqual(self.vm.stack, [9.0])

    def test_stack_underflow_add(self):
        """Test stack underflow for ADD."""
        bytecode = [Instruction.LITERAL, 1, Instruction.ADD]
        with self.assertRaisesRegex(
            ValueError, "Stack underflow during ADD operation."
        ):
            self.vm.interpret(bytecode)

    def test_stack_underflow_subtract(self):
        """Test stack underflow for SUBTRACT."""
        bytecode = [Instruction.SUBTRACT]
        with self.assertRaisesRegex(
            ValueError, "Stack underflow during SUBTRACT operation."
        ):
            self.vm.interpret(bytecode)

    def test_stack_underflow_multiply(self):
        """Test stack underflow for MULTIPLY."""
        bytecode = [Instruction.LITERAL, 5, Instruction.MULTIPLY]
        with self.assertRaisesRegex(
            ValueError, "Stack underflow during MULTIPLY operation."
        ):
            self.vm.interpret(bytecode)

    def test_stack_underflow_divide(self):
        """Test stack underflow for DIVIDE."""
        bytecode = [Instruction.DIVIDE]
        with self.assertRaisesRegex(
            ValueError, "Stack underflow during DIVIDE operation."
        ):
            self.vm.interpret(bytecode)

    def test_division_by_zero(self):
        """Test division by zero."""
        bytecode = [Instruction.LITERAL, 10, Instruction.LITERAL, 0, Instruction.DIVIDE]
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
        bytecode = [Instruction.LITERAL, 10, Instruction.LITERAL, 20]
        result = self.vm.interpret(bytecode)
        # Assuming the VM returns the entire stack if more than one item is left
        self.assertEqual(result, [10, 20])
        self.assertEqual(self.vm.stack, [10, 20])

    # --- Lexer Tests ---
    def test_lexer_single_tokens(self):
        """Test lexer for individual tokens."""
        test_cases = {
            "123": Token(TokenType.NUMBER, 123),
            "3.14": Token(TokenType.NUMBER, 3.14),
            "+": Token(TokenType.PLUS),
            "-": Token(TokenType.MINUS),
            "*": Token(TokenType.MULTIPLY),
            "/": Token(TokenType.DIVIDE),
            "(": Token(TokenType.LPAREN),
            ")": Token(TokenType.RPAREN),
            "  ": Token(
                TokenType.EOF
            ),  # Whitespace should lead to EOF if it's all there is
            "": Token(TokenType.EOF),
        }
        for text, expected_token in test_cases.items():
            with self.subTest(text=text):
                lexer = Lexer(text)
                token = lexer.get_next_token()
                self.assertEqual(token.type, expected_token.type)
                self.assertEqual(token.value, expected_token.value)
                if text.strip():  # If there was non-whitespace, check EOF follows
                    self.assertEqual(lexer.get_next_token().type, TokenType.EOF)

    def test_lexer_sequence(self):
        """Test lexer for a sequence of tokens."""
        lexer = Lexer("(1 + 23) * 4.5")
        expected_tokens = [
            Token(TokenType.LPAREN),
            Token(TokenType.NUMBER, 1),
            Token(TokenType.PLUS),
            Token(TokenType.NUMBER, 23),
            Token(TokenType.RPAREN),
            Token(TokenType.MULTIPLY),
            Token(TokenType.NUMBER, 4.5),
            Token(TokenType.EOF),
        ]
        for expected in expected_tokens:
            token = lexer.get_next_token()
            self.assertEqual(token.type, expected.type)
            self.assertEqual(token.value, expected.value)

    def test_lexer_whitespace_handling(self):
        """Test lexer's handling of whitespace."""
        lexer = Lexer("  5   +   10  ")
        expected_tokens = [
            Token(TokenType.NUMBER, 5),
            Token(TokenType.PLUS),
            Token(TokenType.NUMBER, 10),
            Token(TokenType.EOF),
        ]
        for expected in expected_tokens:
            token = lexer.get_next_token()
            self.assertEqual(token.type, expected.type)
            self.assertEqual(token.value, expected.value)

    def test_lexer_unknown_character(self):
        """Test lexer for unknown character."""
        lexer = Lexer("10 % 5")
        self.assertEqual(lexer.get_next_token(), Token(TokenType.NUMBER, 10))
        with self.assertRaisesRegex(
            SyntaxError, "Unexpected character: '%' at position 3"
        ):
            lexer.get_next_token()

    def test_lexer_invalid_number_format(self):
        """Test lexer for invalid number format like 1.2.3"""
        lexer = Lexer("1.2.3")
        # The number method backtracks, error on first char of invalid part.
        # For "1.2.3", it tries to parse "1", then ".", then "2", then ".", then "3".
        # When it sees the second ".", it backtracks to the start of "1.2.3".
        # The get_next_token then reports an error at the current char '1' at pos 0.
        with self.assertRaisesRegex(
            SyntaxError, "Invalid number format starting with '1' at position 0"
        ):
            lexer.get_next_token()

        lexer_dot_only = Lexer(".")
        with self.assertRaisesRegex(
            SyntaxError, "Invalid number format starting with '.' at position 0"
        ):
            lexer_dot_only.get_next_token()

    # --- Parser Tests ---
    def assert_bytecode_equals(self, generated_bytecode, expected_bytecode):
        self.assertEqual(
            len(generated_bytecode),
            len(expected_bytecode),
            f"Bytecode length mismatch. Got {generated_bytecode}, expected {expected_bytecode}",
        )
        for gen_item, exp_item in zip(generated_bytecode, expected_bytecode):
            if isinstance(gen_item, Instruction) and isinstance(exp_item, Instruction):
                self.assertEqual(gen_item, exp_item)
            elif isinstance(gen_item, (int, float)) and isinstance(
                exp_item, (int, float)
            ):
                self.assertAlmostEqual(
                    gen_item, exp_item, places=7
                )  # For float comparisons
            else:
                self.assertEqual(gen_item, exp_item)

    def test_parser_simple_number(self):
        """Test parsing a single number."""
        lexer = Lexer("42")
        parser = Parser(lexer)
        bytecode = parser.parse()
        expected = [Instruction.LITERAL, 42]
        self.assert_bytecode_equals(bytecode, expected)

    def test_parser_simple_addition(self):
        """Test parsing simple addition."""
        lexer = Lexer("3 + 7")
        parser = Parser(lexer)
        bytecode = parser.parse()
        expected = [Instruction.LITERAL, 3, Instruction.LITERAL, 7, Instruction.ADD]
        self.assert_bytecode_equals(bytecode, expected)

    def test_parser_operator_precedence(self):
        """Test parsing with operator precedence (multiplication before addition)."""
        lexer = Lexer("2 + 3 * 4")
        parser = Parser(lexer)
        bytecode = parser.parse()
        # Expected: 2, 3, 4, MULTIPLY, ADD
        expected = [
            Instruction.LITERAL,
            2,
            Instruction.LITERAL,
            3,
            Instruction.LITERAL,
            4,
            Instruction.MULTIPLY,
            Instruction.ADD,
        ]
        self.assert_bytecode_equals(bytecode, expected)

    def test_parser_parentheses(self):
        """Test parsing with parentheses to override precedence."""
        lexer = Lexer("(2 + 3) * 4")
        parser = Parser(lexer)
        bytecode = parser.parse()
        # Expected: 2, 3, ADD, 4, MULTIPLY
        expected = [
            Instruction.LITERAL,
            2,
            Instruction.LITERAL,
            3,
            Instruction.ADD,
            Instruction.LITERAL,
            4,
            Instruction.MULTIPLY,
        ]
        self.assert_bytecode_equals(bytecode, expected)

    def test_parser_complex_expression(self):
        """Test parsing a more complex expression."""
        # (10 - 2) / (1 + 3) * 5.5
        # Expected: 10, 2, SUB, 1, 3, ADD, DIV, 5.5, MUL
        lexer = Lexer("(10 - 2.0) / (1 + 3) * 5.5")
        parser = Parser(lexer)
        bytecode = parser.parse()
        expected = [
            Instruction.LITERAL,
            10,
            Instruction.LITERAL,
            2.0,
            Instruction.SUBTRACT,
            Instruction.LITERAL,
            1,
            Instruction.LITERAL,
            3,
            Instruction.ADD,
            Instruction.DIVIDE,
            Instruction.LITERAL,
            5.5,
            Instruction.MULTIPLY,
        ]
        self.assert_bytecode_equals(bytecode, expected)

    def test_parser_syntax_error_unexpected_token(self):
        """Test parser for syntax error: unexpected token."""
        lexer = Lexer("5 + * 2")
        parser = Parser(lexer)
        # Error occurs when parser.term() tries to process factor after MULTIPLY
        # and finds another MULTIPLY instead of a NUMBER or LPAREN.
        # Lexer pos will be after the second '*' (index 4, so pos 5)
        with self.assertRaisesRegex(
            SyntaxError,
            "Factor expected a NUMBER or LPAREN near token Token\\(MULTIPLY, None\\) \\(pos ~5\\)",
        ):
            parser.parse()

    def test_parser_syntax_error_mismatched_parentheses_unclosed(self):
        """Test parser for syntax error: unclosed parenthesis."""
        lexer = Lexer("(10 + 5")  # Length 7, lexer.pos will be 7
        parser = Parser(lexer)
        with self.assertRaisesRegex(
            SyntaxError, "Expected token RPAREN but got EOF \\(pos ~7\\)"
        ):
            parser.parse()

    def test_parser_syntax_error_mismatched_parentheses_unexpected_closing(self):
        """Test parser for syntax error: unexpected closing parenthesis."""
        lexer = Lexer("10 + 5)")  # Length 7, lexer.pos will be 7
        parser = Parser(lexer)
        # The parser will successfully parse "10 + 5" and then hit the RPAREN.
        with self.assertRaisesRegex(
            SyntaxError,
            "Unexpected token at end of expression near token Token\\(RPAREN, None\\) \\(pos ~7\\)",
        ):
            parser.parse()

    def test_parser_syntax_error_incomplete_expression(self):
        """Test parser for syntax error: incomplete expression."""
        lexer = Lexer("7 + ")  # Length 4, lexer.pos will be 4
        parser = Parser(lexer)
        # Error occurs when parser.term() expects a factor after PLUS but gets EOF.
        with self.assertRaisesRegex(
            SyntaxError, "Factor expected a NUMBER or LPAREN \\(pos ~4\\)"
        ):
            parser.parse()

    def test_parser_syntax_error_leading_operator(self):
        """Test parser for syntax error: expression starting with an operator."""
        lexer = Lexer("* 2 + 3")  # lexer.pos will be 1 after '*'
        parser = Parser(lexer)
        # Error occurs when parser.factor() (called by term, then expr) expects NUMBER or LPAREN.
        with self.assertRaisesRegex(
            SyntaxError,
            "Factor expected a NUMBER or LPAREN near token Token\\(MULTIPLY, None\\) \\(pos ~1\\)",
        ):
            parser.parse()

    def test_parser_syntax_error_trailing_operator(self):
        """Test parser for syntax error: expression ending with an operator."""
        lexer = Lexer("2 + 3 *")  # Length 7, lexer.pos will be 7
        parser = Parser(lexer)
        # Error occurs when parser.factor() (called by term after MULTIPLY) expects NUMBER or LPAREN but gets EOF.
        with self.assertRaisesRegex(
            SyntaxError, "Factor expected a NUMBER or LPAREN \\(pos ~7\\)"
        ):
            parser.parse()


if __name__ == "__main__":
    unittest.main()
