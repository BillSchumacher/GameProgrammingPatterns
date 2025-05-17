from enum import Enum, auto
import dataclasses


class Instruction(Enum):
    """Defines the available instructions for the VM."""

    LITERAL = auto()  # Push a literal value onto the stack
    ADD = auto()  # Pop two values, add them, push result
    SUBTRACT = auto()  # Pop two values, subtract them, push result
    MULTIPLY = auto()  # Pop two values, multiply them, push result
    DIVIDE = auto()  # Pop two values, divide them, push result
    # Add more instructions as needed, e.g., for control flow, memory access


# New: Token types for the lexer
class TokenType(Enum):
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()  # End of File/Input


@dataclasses.dataclass
class Token:
    type: TokenType
    value: any = None

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)})"


class Lexer:
    """Breaks an input string into a stream of tokens."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def advance(self):
        """Advance the 'pos' pointer and set 'current_char'."""
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        """Return a (multidigit) integer or float consumed from the input."""
        result = ""
        while self.current_char is not None and (
            self.current_char.isdigit() or self.current_char == "."
        ):
            result += self.current_char
            self.advance()

        if "." in result:
            try:
                return float(result)
            except ValueError:
                for _ in result:  # backtrack
                    self.pos -= 1
                self.current_char = self.text[self.pos]
                return None  # Signal an issue
        else:
            try:
                return int(result)
            except ValueError:
                return None  # Signal an issue

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)."""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit() or self.current_char == ".":
                num_val = self.number()
                if num_val is not None:
                    return Token(TokenType.NUMBER, num_val)
                else:
                    raise SyntaxError(
                        f"Invalid number format starting with '{self.current_char}' at position {self.pos}"
                    )

            if self.current_char == "+":
                self.advance()
                return Token(TokenType.PLUS)
            if self.current_char == "-":
                self.advance()
                return Token(TokenType.MINUS)
            if self.current_char == "*":
                self.advance()
                return Token(TokenType.MULTIPLY)
            if self.current_char == "/":
                self.advance()
                return Token(TokenType.DIVIDE)
            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN)
            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN)

            raise SyntaxError(
                f"Unexpected character: '{self.current_char}' at position {self.pos}"
            )

        return Token(TokenType.EOF)


class Parser:
    """
    Parses a stream of tokens into bytecode.
    Implements a simple recursive descent parser for arithmetic expressions:
    expr   : term ((PLUS | MINUS) term)*
    term   : factor ((MULTIPLY | DIVIDE) factor)*
    factor : NUMBER | LPAREN expr RPAREN
    """

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.bytecode = []

    def error(self, message="Invalid syntax"):
        if self.current_token and self.current_token.type != TokenType.EOF:
            raise SyntaxError(
                f"{message} near token {self.current_token} (pos ~{self.lexer.pos})"
            )
        else:
            raise SyntaxError(f"{message} (pos ~{self.lexer.pos})")

    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(
                f"Expected token {token_type.name} but got {self.current_token.type.name}"
            )

    def factor(self):
        """factor : NUMBER | LPAREN expr RPAREN"""
        token = self.current_token
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            self.bytecode.append(Instruction.LITERAL)
            self.bytecode.append(token.value)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            self.expr()
            self.eat(TokenType.RPAREN)
        else:
            self.error("Factor expected a NUMBER or LPAREN")

    def term(self):
        """term : factor ((MULTIPLY | DIVIDE) factor)*"""
        self.factor()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op_token = self.current_token
            if op_token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
                self.factor()
                self.bytecode.append(Instruction.MULTIPLY)
            elif op_token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
                self.factor()
                self.bytecode.append(Instruction.DIVIDE)

    def expr(self):
        """expr : term ((PLUS | MINUS) term)*"""
        self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.current_token
            if op_token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                self.term()
                self.bytecode.append(Instruction.ADD)
            elif op_token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
                self.term()
                self.bytecode.append(Instruction.SUBTRACT)

    def parse(self):
        self.expr()
        if self.current_token.type != TokenType.EOF:
            self.error("Unexpected token at end of expression")
        return self.bytecode


class VirtualMachine:
    """Executes a sequence of bytecode instructions."""

    def __init__(self):
        self.stack = []
        self.ip = 0  # Instruction pointer

    def interpret(self, bytecode: list):
        """
        Interprets and executes the given bytecode.
        Bytecode is a list where instructions are followed by their arguments
        if any. For example: [Instruction.LITERAL, 5, Instruction.LITERAL, 10, Instruction.ADD]
        """
        self.ip = 0
        while self.ip < len(bytecode):
            instruction = bytecode[self.ip]
            self.ip += 1

            if instruction == Instruction.LITERAL:
                value = bytecode[self.ip]
                self.ip += 1
                self.stack.append(value)
            elif instruction == Instruction.ADD:
                if len(self.stack) < 2:
                    raise ValueError("Stack underflow during ADD operation.")
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(left + right)
            elif instruction == Instruction.SUBTRACT:
                if len(self.stack) < 2:
                    raise ValueError("Stack underflow during SUBTRACT operation.")
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(left - right)
            elif instruction == Instruction.MULTIPLY:
                if len(self.stack) < 2:
                    raise ValueError("Stack underflow during MULTIPLY operation.")
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(left * right)
            elif instruction == Instruction.DIVIDE:
                if len(self.stack) < 2:
                    raise ValueError("Stack underflow during DIVIDE operation.")
                right = self.stack.pop()
                left = self.stack.pop()
                if right == 0:
                    raise ZeroDivisionError("Division by zero.")
                self.stack.append(left / right)  # Or use // for integer division
            else:
                raise ValueError(f"Unknown instruction: {instruction}")

        if len(self.stack) == 1:
            return self.stack[0]
        elif len(self.stack) > 1:
            return self.stack
        return None


def example():
    """Example usage of the Bytecode pattern."""
    vm = VirtualMachine()

    # Expression to parse and execute: (5 + 10) * 2
    expression1 = "(5 + 10) * 2"
    print(f"Parsing expression: '{expression1}'")
    try:
        lexer1 = Lexer(expression1)
        parser1 = Parser(lexer1)
        bytecode1 = parser1.parse()
        print(
            f"Generated Bytecode: {bytecode1}"
        )  # e.g., [LITERAL, 5, LITERAL, 10, ADD, LITERAL, 2, MULTIPLY]

        result1 = vm.interpret(bytecode1)
        print(f"Executing '{expression1}': Result = {result1}")  # Expected: 30
    except SyntaxError as e:
        print(f"Syntax Error for '{expression1}': {e}")
    except ValueError as e:  # From VM
        print(f"VM Error for '{expression1}': {e}")
    except ZeroDivisionError as e:  # From VM
        print(f"VM Error for '{expression1}': {e}")

    # Reset VM for next calculation
    vm = VirtualMachine()
    expression2 = "100 / (25 - 5)"
    print(f"\nParsing expression: '{expression2}'")
    try:
        lexer2 = Lexer(expression2)
        parser2 = Parser(lexer2)
        bytecode2 = parser2.parse()
        print(f"Generated Bytecode: {bytecode2}")
        result2 = vm.interpret(bytecode2)
        print(f"Executing '{expression2}': Result = {result2}")  # Expected: 5.0
    except SyntaxError as e:
        print(f"Syntax Error for '{expression2}': {e}")
    except ValueError as e:  # From VM
        print(f"VM Error for '{expression2}': {e}")
    except ZeroDivisionError as e:  # From VM
        print(f"VM Error for '{expression2}': {e}")

    # Example with a syntax error
    vm = VirtualMachine()
    expression_err = "5 + * 2"  # Invalid syntax
    print(f"\nParsing expression: '{expression_err}'")
    try:
        lexer_err = Lexer(expression_err)
        parser_err = Parser(lexer_err)
        bytecode_err = parser_err.parse()
        result_err = vm.interpret(bytecode_err)
        print(f"Executing '{expression_err}': Result = {result_err}")
    except SyntaxError as e:
        print(f"Syntax Error for '{expression_err}': {e}")  # Expected
    except ValueError as e:
        print(f"VM Error for '{expression_err}': {e}")
    except ZeroDivisionError as e:
        print(f"VM Error for '{expression_err}': {e}")

    # Example with an unknown character
    vm = VirtualMachine()
    expression_unknown_char = "10 % 2"
    print(f"\nParsing expression: '{expression_unknown_char}'")
    try:
        lexer_unknown = Lexer(expression_unknown_char)
        parser_unknown = Parser(lexer_unknown)
        bytecode_unknown = parser_unknown.parse()
        result_unknown = vm.interpret(bytecode_unknown)
        print(f"Executing '{expression_unknown_char}': Result = {result_unknown}")
    except SyntaxError as e:
        print(f"Syntax Error for '{expression_unknown_char}': {e}")  # Expected
    except ValueError as e:
        print(f"VM Error for '{expression_unknown_char}': {e}")
    except ZeroDivisionError as e:
        print(f"VM Error for '{expression_unknown_char}': {e}")

    # Example with mismatched parentheses
    vm = VirtualMachine()
    expression_paren_err = "(10 + 5"
    print(f"\nParsing expression: '{expression_paren_err}'")
    try:
        lexer_paren = Lexer(expression_paren_err)
        parser_paren = Parser(lexer_paren)
        bytecode_paren = parser_paren.parse()
        result_paren = vm.interpret(bytecode_paren)
        print(f"Executing '{expression_paren_err}': Result = {result_paren}")
    except SyntaxError as e:
        print(f"Syntax Error for '{expression_paren_err}': {e}")  # Expected
    except ValueError as e:
        print(f"VM Error for '{expression_paren_err}': {e}")
    except ZeroDivisionError as e:
        print(f"VM Error for '{expression_paren_err}': {e}")


if __name__ == "__main__":
    example()
