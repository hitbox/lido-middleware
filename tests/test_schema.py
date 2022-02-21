import unittest

from schema import only_digits
from schema import mid_digits

class TestOnlyDigits(unittest.TestCase):
    """
    Keep only digits and remove leading zeros, keeping as string.
    """

    def test_intstr_empty(self):
        self.assertEqual(only_digits(''), '')

    def test_intstr_onlydigits(self):
        self.assertEqual(only_digits('123'), '123')
        self.assertEqual(only_digits('012'), '12')
        # keep trailing zero
        self.assertEqual(only_digits('120'), '120')
        self.assertEqual(only_digits('000'), '')

    def test_intstr_onlyalpha(self):
        self.assertEqual(only_digits('abc'), '')

    def test_intstr_mixed(self):
        self.assertEqual(only_digits('abc123'), '123')
        self.assertEqual(only_digits('abc012'), '12')
        self.assertEqual(only_digits('abc120'), '120')
        self.assertEqual(only_digits('abc000'), '')
        #
        self.assertEqual(only_digits('123def'), '123')
        self.assertEqual(only_digits('012def'), '12')
        self.assertEqual(only_digits('120def'), '120')
        self.assertEqual(only_digits('000def'), '')
        #
        self.assertEqual(only_digits('abc123def'), '123')
        self.assertEqual(only_digits('abc012def'), '12')
        self.assertEqual(only_digits('abc120def'), '120')
        self.assertEqual(only_digits('abc010def'), '10')
        self.assertEqual(only_digits('abc000def'), '')


class TestMidDigits(unittest.TestCase):

    def test_mid_digits_empty(self):
        self.assertEqual(mid_digits(''), '')

    def test_mid_digits_onlydigits(self):
        self.assertEqual(mid_digits('123'), '123')
        self.assertEqual(mid_digits('012'), '12')
        self.assertEqual(mid_digits('120'), '120')

    def test_mid_digits_onlyalpha(self):
        self.assertEqual(mid_digits('abc'), '')

    def test_mid_digits_mixed(self):
        self.assertEqual(mid_digits('abc123'), '123')
        self.assertEqual(mid_digits('abc012'), '12')
        self.assertEqual(mid_digits('abc120'), '120')
        self.assertEqual(mid_digits('abc000'), '')
        #
        self.assertEqual(mid_digits('123def'), '123')
        self.assertEqual(mid_digits('012def'), '12')
        self.assertEqual(mid_digits('120def'), '120')
        self.assertEqual(mid_digits('000def'), '')
        #
        self.assertEqual(mid_digits('abc123def'), '123')
        self.assertEqual(mid_digits('abc012def'), '12')
        self.assertEqual(mid_digits('abc120def'), '120')
        self.assertEqual(mid_digits('abc010def'), '10')
        self.assertEqual(mid_digits('abc000def'), '')

    def test_mid_digits_trailing_digits(self):
        # additional problem to be solved of digits after alpha chars on end
        self.assertEqual(mid_digits('123def01'), '123')
        self.assertEqual(mid_digits('012def01'), '12')
        self.assertEqual(mid_digits('120def01'), '120')
        self.assertEqual(mid_digits('000def01'), '')
        #
        self.assertEqual(mid_digits('abc123def123'), '123')
        self.assertEqual(mid_digits('abc012def123'), '12')
        self.assertEqual(mid_digits('abc120def123'), '120')
        self.assertEqual(mid_digits('abc010def123'), '10')
        self.assertEqual(mid_digits('abc000def123'), '')


if __name__ == '__main__':
    unittest.main()
