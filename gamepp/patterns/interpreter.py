from abc import ABC, abstractmethod


class Expression(ABC):
    @abstractmethod
    def interpret(self) -> float:
        pass


class NumberExpression(Expression):
    def __init__(self, value: float):
        self._value = value

    def interpret(self) -> float:
        return self._value


class AddExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right

    def interpret(self) -> float:
        return self._left.interpret() + self._right.interpret()


class SubtractExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right

    def interpret(self) -> float:
        return self._left.interpret() - self._right.interpret()


class MultiplyExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right

    def interpret(self) -> float:
        return self._left.interpret() * self._right.interpret()


class DivideExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right

    def interpret(self) -> float:
        right_val = self._right.interpret()
        if right_val == 0:
            raise ValueError("Cannot divide by zero.")
        return self._left.interpret() / right_val
