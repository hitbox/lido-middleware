import unittest

from pathlib import Path

import sable.extract

class TestLIDO(unittest.TestCase):

    def test_sable_extract(self):
        thisdir = Path(__file__).parent / 'data'
        message_path = thisdir / 'sable_message.txt'
        extract_path = thisdir / 'sable_message.txt.extract-expect.py'
        with open(message_path) as sable_file, \
                open(extract_path) as extract_file:
            expects = eval(extract_file.read())
            loadplan_data = sable.extract.from_text(sable_file.read())
            self.assertEqual(loadplan_data, expects)


if __name__ == '__main__':
    unittest.main()
