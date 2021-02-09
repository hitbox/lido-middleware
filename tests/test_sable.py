import unittest

from pathlib import Path

import lido
import sable.extract
import sable.schema

datadir = Path(__file__).parent / 'data'

class TestSableExtract(unittest.TestCase):

    def test_sable_extract(self):
        """
        Test extracting strings from a sable message.
        """
        message_path = datadir / 'sable_message.txt'
        extract_path = datadir / 'sable_message.txt.extract-expect.py'
        with open(message_path) as sable_file, \
                open(extract_path) as extract_file:
            expects = eval(extract_file.read())
            loadplan_data = sable.extract.from_text(sable_file.read())
            self.maxDiff = None
            self.assertEqual(loadplan_data, expects)


class TestSableSchema(unittest.TestCase):

    def test_sable_extract(self):
        """
        Test converting extracted strings into data types.
        """
        schema = sable.schema.LoadPlanSchema()
        message_path = datadir / 'sable_message.txt.extract-expect.py'
        schema_path = datadir / 'sable_message.txt.schema-load-expect.py'
        with open(message_path) as sable_file, \
                open(schema_path) as schema_file:
            expects = eval(schema_file.read())
            loadplan_data = eval(sable_file.read())
            loadplan = schema.load(loadplan_data)
            self.maxDiff = None
            self.assertEqual(loadplan, expects)


class TestSableLIDO(unittest.TestCase):

    @unittest.skip('schema load and a/c reg. to airline is unfinished and'
                   ' actual_takeoff_fuel, actual_zero_fuel_weight,'
                   ' center_of_gravity, and dry_operating_weight is unknown')
    def test_sable_message_to_lido_string(self):
        loadplan_schema = LoadPlanSchema()
        loadplan_path = datadir / 'sable_message.txt.schema-load-expect.py'
        with open(loadplan_path) as loadplan_file:
            loadplan = eval(loadplan_file.read())
            wbmsg = LIDOWeightBalanceMessage(loadplan)
            s = str(wbmsg)
            print(s)
            #e = ('WAB09NOV2017002500COM  123 09NOV2017MIA  NGU  04100'
            #     '      000000NNN 24.121487521783520000L     017986  '
            #     '                            ')
            #self.assertEqual(s, e)


if __name__ == '__main__':
    unittest.main()
