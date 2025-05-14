import unittest
from gpp.patterns.interpreter import (
    NumberExpression, AddExpression, SubtractExpression, 
    MultiplyExpression, DivideExpression
)

class TestInterpreterPattern(unittest.TestCase):

    def test_number_expression(self):
        expression = NumberExpression(10)
        self.assertEqual(expression.interpret(), 10)

    def test_add_expression(self):
        expression = AddExpression(NumberExpression(5), NumberExpression(3))
        self.assertEqual(expression.interpret(), 8)

    def test_subtract_expression(self):
        expression = SubtractExpression(NumberExpression(10), NumberExpression(4))
        self.assertEqual(expression.interpret(), 6)

    def test_multiply_expression(self):
        expression = MultiplyExpression(NumberExpression(3), NumberExpression(7))
        self.assertEqual(expression.interpret(), 21)

    def test_divide_expression(self):
        expression = DivideExpression(NumberExpression(20), NumberExpression(5))
        self.assertEqual(expression.interpret(), 4)

    def test_divide_by_zero(self):
        expression = DivideExpression(NumberExpression(10), NumberExpression(0))
        with self.assertRaises(ValueError) as context:
            expression.interpret()
        self.assertEqual(str(context.exception), "Cannot divide by zero.")

    def test_complex_expression(self):
        # (1 + 2) * (3 - 4)
        # Expected: 3 * -1 = -3
        add_expr = AddExpression(NumberExpression(1), NumberExpression(2))  # 1 + 2 = 3
        sub_expr = SubtractExpression(NumberExpression(3), NumberExpression(4)) # 3 - 4 = -1
        complex_expr = MultiplyExpression(add_expr, sub_expr) # 3 * -1 = -3
        self.assertEqual(complex_expr.interpret(), -3)

    def test_more_complex_expression(self):
        # ( (10 / 2) + (3 * 4) ) - 7
        # Expected: (5 + 12) - 7 = 17 - 7 = 10
        div_expr = DivideExpression(NumberExpression(10), NumberExpression(2)) # 10 / 2 = 5
        mul_expr = MultiplyExpression(NumberExpression(3), NumberExpression(4)) # 3 * 4 = 12
        add_expr = AddExpression(div_expr, mul_expr) # 5 + 12 = 17
        complex_expr = SubtractExpression(add_expr, NumberExpression(7)) # 17 - 7 = 10
        self.assertEqual(complex_expr.interpret(), 10)

if __name__ == '__main__':
    unittest.main()
