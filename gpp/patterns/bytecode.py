"""
Bytecode Pattern:

An instruction set defines the low-level operations that can be performed.
A series of instructions is encoded as a sequence of bytes. A virtual
machine executes these instructions one at a time, using a stack for
intermediate values. By combining instructions, complex high-level
behavior can be defined.
"""

from enum import Enum, auto

class Instruction(Enum):
    """Defines the available instructions for the VM."""
    LITERAL = auto()  # Push a literal value onto the stack
    ADD = auto()      # Pop two values, add them, push result
    SUBTRACT = auto() # Pop two values, subtract them, push result
    MULTIPLY = auto() # Pop two values, multiply them, push result
    DIVIDE = auto()   # Pop two values, divide them, push result
    # Add more instructions as needed, e.g., for control flow, memory access

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
                self.stack.append(left / right) # Or use // for integer division
            else:
                raise ValueError(f"Unknown instruction: {instruction}")
        
        if len(self.stack) == 1:
            return self.stack[0]
        elif len(self.stack) > 1:
            # Or handle this case as an error, depending on expected behavior
            return self.stack 
        return None # Or raise error if stack is empty and a result was expected

def example():
    """Example usage of the Bytecode pattern."""
    vm = VirtualMachine()

    # (5 + 10) * 2
    bytecode = [
        Instruction.LITERAL, 5,
        Instruction.LITERAL, 10,
        Instruction.ADD,
        Instruction.LITERAL, 2,
        Instruction.MULTIPLY
    ]
    result = vm.interpret(bytecode)
    print(f"Executing (5 + 10) * 2: Result = {result}") # Expected: 30

    # Reset VM for next calculation or use a new instance
    vm = VirtualMachine() 
    # 100 / (25 - 5)
    bytecode_div = [
        Instruction.LITERAL, 100,
        Instruction.LITERAL, 25,
        Instruction.LITERAL, 5,
        Instruction.SUBTRACT,
        Instruction.DIVIDE
    ]
    result_div = vm.interpret(bytecode_div)
    print(f"Executing 100 / (25 - 5): Result = {result_div}") # Expected: 5.0

if __name__ == "__main__":
    example()
