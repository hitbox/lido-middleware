import unittest

from pathlib import Path

import sable.schema

class TestSableLoadPlanSchema(unittest.TestCase):

    def test_sable_extract(self):
        schema = sable.schema.LoadPlanSchema()
        datadir = Path(__file__).parent / 'data'
        message_path = datadir / 'sable_message.txt.extract-expect.py'
        schema_path = datadir / 'sable_message.txt.schema-load-expect.py'
        with open(message_path) as sable_file, \
                open(schema_path) as schema_file:
            expects = eval(schema_file.read())
            loadplan_data = eval(sable_file.read())
            loadplan = schema.load(loadplan_data)
            self.assertEqual(loadplan, expects)


if __name__ == '__main__':
    unittest.main()
