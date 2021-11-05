import unittest

from utils import sliding_match

class TestSlidingMatch(unittest.TestCase):

    def test_sliding_match(self):
        self.assertEqual(sliding_match('abc', 'abc'), 0)
        self.assertEqual(sliding_match('abc', '--abc--'), 2)
        self.assertEqual(sliding_match('a b c d', 'a-b-c-d'), 0)
        self.assertEqual(sliding_match('a b c d', 'a-b-c-d remaining'), 0)
        self.assertEqual(sliding_match('a b c d', 'before text a-b-c-d remaining'), 12)


if __name__ == '__main__':
    unittest.main()
