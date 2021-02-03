import unittest

from datetime import datetime
from pathlib import Path

import pistol.schema

class TestPistolSchema(unittest.TestCase):

    def test_pistol_schema_load(self):
        datadir = Path(__file__).parent / 'data'
        extracted_path = datadir / 'pistol_message.txt.extract-expect.py'
        expect_path = datadir / 'pistol_message.txt.schema-load-expect.py'
        with open(extracted_path) as extracted_file, \
                open(expect_path) as expected_file:
            extracted_data = eval(extracted_file.read(), {'datetime': datetime})
            expected = eval(expected_file.read())
            loadplan = pistol.schema.LoadPlanSchema().load(extracted_data)
            self.maxDiff = None
            self.assertEqual(loadplan, expected)


if __name__ == '__main__':
    unittest.main()
