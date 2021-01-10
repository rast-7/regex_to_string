import random
import re
import unittest
from .__init__ import StringGenerator

class TestStringGenerator(unittest.TestCase):
    def test_string_generator(self):
        """Test various templates"""
        test_list = [
            "[a-z]{10}(.|_)[a-z]{5,10}@[a-z]{3,12}.(com|net|org)",
            "[a-z1234]{8}",
            "([a-z]{4}|[0-9]{9})",
            "[-+]?[0-9]{1,16}[.][0-9]{1,6}",
            "(1[0-2])|(0[1-9])(:[0-5][0-9]){2} (A|P)M"
        ]

        for test in test_list:
            result = StringGenerator(test).render()
            self.assertIsNotNone(result)
            print(result)
            print(bool(re.match(test, result)))
            self.assertTrue(bool(re.match(test, result)))

    def test_syntax_exceptions(self):
        """Make sure syntax errors in template are caught."""
        test_list = [
            "[a-z]{a}", # Not a valid quantifier
            "[a-]", # Invalid class range
            "[[1-9]", # Unescaped chars
            "((foo)(bar)))", # Extra parens
            "|foo", # Binary operator error
            "[1-10]{6:}", # Cannot have an open range quantifier
        ]
        for test in test_list:
            self.assertRaises(
                StringGenerator.SyntaxError, lambda: StringGenerator(test).render()
            )

    def test_uniqueness_error(self):
        """Make sure we throw an exception if we can't generate list"""
        test = "[123]"
        self.assertRaises(
            StringGenerator.UniquenessError,
            lambda: StringGenerator(test).render_list(100, unique=True)
        )

    def test_literals(self):
        """Test various literals"""
        test_list = ["hel-lo[abcdefghi]{4}", "colou?r"]

        for test in test_list:
            result = StringGenerator(test).render()
            self.assertIsNotNone(result)
            self.assertTrue(bool(re.match(test, result)))


if __name__ == "__main__":
    unittest.main()
