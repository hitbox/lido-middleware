import unittest

from datetime import datetime
from pathlib import Path

import lido
import pistol.extract
import pistol.schema

datadir = Path(__file__).parent / 'data'

class TestPistolExtract(unittest.TestCase):

    def test_pistol_schema_funcs(self):
        self.assertEqual(
            pistol.schema.split_company_and_flight_number('ABX1234'),
            ('ABX', '1234'))
        self.assertEqual(
            pistol.schema.split_company_and_flight_number('ABX_TAKELASTFOUR_1234'),
            ('ABX', '1234'))
        # this one below will change, this is not what they want
        self.assertEqual(
            pistol.schema.split_company_and_flight_number('ABXCMBDQ1'),
            ('ABX', 'BDQ1'))

    def test_pistol_extract(self):
        """
        Test extracting strings from pistol message.
        """
        message_path = datadir / 'pistol_message.txt'
        expect_path = datadir / 'pistol_message.txt.extract-expect.py'
        with open(message_path) as pistol_message_file, \
                open(expect_path) as pistol_expected_file:
            message_text = pistol_message_file.read()
            expects = eval(pistol_expected_file.read())
            actual = pistol.extract.loadplan_from_text(message_text)
            self.assertDictEqual(actual, expects)

    def test_parse_position(self):
        # dot nill
        self.assertDictEqual(
            pistol.extract._position('-A1.NIL'),
            dict(position = 'A1'))
        # normal expected
        self.assertDictEqual(
            pistol.extract._position('-A2L/AAA00000AA/NGU/200LB/A'),
            dict(position = 'A2L',
                 unit_load_device = 'AAA00000AA',
                 destination_iata_or_icao = 'NGU',
                 weight = '200',
                 weight_unit = 'LB',
                 building = 'A'))
        # allow missing and strip whitespace
        self.assertDictEqual(
            pistol.extract._position('-A3L/CCC00000CC/ /300LB/B'),
            dict(position = 'A3L',
                 unit_load_device = 'CCC00000CC',
                 destination_iata_or_icao = ' ',
                 weight = '300',
                 weight_unit = 'LB',
                 building = 'B'))
        # enforce format: does not start with dash
        with self.assertRaises(pistol.extract.ExtractError):
            pistol.extract._position('A4/DDD00000DD/ /200LB/A')
        # enforce format: must not contain newlines
        with self.assertRaises(pistol.extract.ExtractError):
            pistol.extract._position('-A5/EEE00000EE/FFF/200LB/A\n-A6/FFF00000FF/GGG/201LB/A')
        # enforce weight units: must be LB or KG
        with self.assertRaises(pistol.extract.ExtractError):
            pistol.extract._position('-A5/HHH00000HH/ /123__/A')

    def test_parse__flight_number_and_company(self):
        # function parses string and return flight number and company tuple
        self.assertEqual(pistol.extract._flight_number_and_company('AAA1234'), ('1234', 'AAA'))
        self.assertEqual(pistol.extract._flight_number_and_company('AAA100'), ('100', 'AAA'))
        # this is the current behavior, almost certainely not desired.
        self.assertEqual(pistol.extract._flight_number_and_company('ATIATN100'), ('100', 'ATI'))


class TestPistolSchema(unittest.TestCase):

    def test_pistol_schema_load(self):
        extracted_path = datadir / 'pistol_message.txt.extract-expect.py'
        expect_path = datadir / 'pistol_message.txt.schema-load-expect.py'
        with open(extracted_path) as extracted_file, \
                open(expect_path) as expected_file:
            extracted_data = eval(extracted_file.read(), {'datetime': datetime})
            expected = eval(expected_file.read())
            loadplan = pistol.schema.LoadPlanSchema().load(extracted_data)
            self.maxDiff = None
            self.assertEqual(loadplan, expected)


class TestPistolLIDO(unittest.TestCase):

    def test_pistol_message_to_lido_string(self):
        pistol_loadplan_path = datadir / 'pistol_message.txt.schema-load-expect.py'
        with open(pistol_loadplan_path) as loadplan_file:
            loadplan = eval(loadplan_file.read(), {'datetime': datetime})
            wbmsg = lido.LIDOWeightBalanceMessage(loadplan)
            wbmsg_string = str(wbmsg)
            expects = (
                'WAB09NOV20170025008C   123 09NOV2017MIA  NGU  04100'
                '      000000YYY 24.121487521783520000L     017986  '
                '                            ')
            self.assertEqual(wbmsg_string, expects)


if __name__ == '__main__':
    unittest.main()
