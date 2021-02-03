import unittest

from pathlib import Path

import pistol.extract

class TestPistolExtract(unittest.TestCase):

    def test_pistol_extract(self):
        datadir = Path(__file__).parent / 'data'
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


if __name__ == '__main__':
    unittest.main()
