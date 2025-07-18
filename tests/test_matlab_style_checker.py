import unittest

from pymatlabparser.matlab_style_checker import MatlabStyleChecker

class TestMatlabStyleChecker(unittest.TestCase):
    def setUp(self):
        self.checker = MatlabStyleChecker()

    def test_command_syntax(self):
        code = "disp hello\n"
        errors = self.checker.check_text(code)
        self.assertTrue(any("command syntax" in e for e in errors))

    def test_keyword_spacing(self):
        code = "if(a==1)\nend\n"
        errors = self.checker.check_text(code)
        self.assertTrue(any("keyword 'if'" in e for e in errors))

    def test_comma_spacing(self):
        code = "a = [1 ,2];\n"
        errors = self.checker.check_text(code)
        self.assertTrue(any("comma should not be preceded" in e for e in errors))
        self.assertTrue(any("comma should be followed" in e for e in errors))

    def test_semicolon_spacing(self):
        code = "a = 1;b = 2;\n"
        errors = self.checker.check_text(code)
        self.assertTrue(any("semicolon" in e for e in errors))

    def test_operator_spacing(self):
        code = "a=1+2;\n"
        errors = self.checker.check_text(code)
        self.assertTrue(any("operator '='" in e for e in errors))
        self.assertTrue(any("operator '+'" in e for e in errors))

    def test_unary_minus_spacing(self):
        code = "b = - 1;\n"
        errors = self.checker.check_text(code)
        self.assertTrue(any("unary minus" in e for e in errors))

    def test_function_indentation(self):
        code = "function y = foo(x)\ny = x + 1;\nend\n"
        errors = self.checker.check_text(code)
        self.assertTrue(any("function body" in e for e in errors))

    def test_no_false_positives(self):
        code = "function y = foo(x)\n    if x > 0\n        y = x + 1;\n    else\n        y = x - 1;\n    end\nend\n"
        errors = self.checker.check_text(code)
        self.assertEqual(errors, [])

if __name__ == '__main__':
    unittest.main()
