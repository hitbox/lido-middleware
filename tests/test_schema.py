import unittest

from schema import intstr

class TestIntegerString(unittest.TestCase):

    def test_intstr_empty(self):
        self.assertEqual(intstr(''), '')

    def test_intstr_onlydigits(self):
        self.assertEqual(intstr('123'), '123')
        self.assertEqual(intstr('012'), '12')
        # keep trailing zero
        self.assertEqual(intstr('120'), '120')
        self.assertEqual(intstr('000'), '')

    def test_intstr_onlyalpha(self):
        self.assertEqual(intstr('abc'), '')

    def test_intstr_mixed(self):
        self.assertEqual(intstr('abc123'), '123')
        self.assertEqual(intstr('abc012'), '12')
        self.assertEqual(intstr('abc120'), '120')
        self.assertEqual(intstr('abc000'), '')
        #
        self.assertEqual(intstr('123def'), '123')
        self.assertEqual(intstr('012def'), '12')
        self.assertEqual(intstr('120def'), '120')
        self.assertEqual(intstr('000def'), '')
        #
        self.assertEqual(intstr('abc123def'), '123')
        self.assertEqual(intstr('abc012def'), '12')
        self.assertEqual(intstr('abc120def'), '120')
        self.assertEqual(intstr('abc010def'), '10')
        self.assertEqual(intstr('abc000def'), '')


if __name__ == '__main__':
    unittest.main()
