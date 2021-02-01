import unittest

from pistol import parse

class TestParse(unittest.TestCase):

    def test_parse_load_plan(self):
        # confirm parsing of anonymized load plan text
        expect = dict(
            load_planner = 'LPNAME<lpname@company.com>',
            company = 'COM',
            flight_number = '123',
            aircraft_registration = 'N000ZZ',
            # remember this is the parser, it does not fill the other station
            # type field but it doesn default it to None.
            origin_iata = None,
            origin_icao = 'KMIA',
            destination_iata = None,
            destination_icao = 'KNGU',
            day = '09',
            actual_departure_time = None,
            color_code = 'B PURPLE',
            souls_onboard = '19',
            all_weights_unit = 'LB',
            # meta data
            pistol_version = 'PSTL_1900.01.01.0001',
            computer = 'COMPUTER1',
            print_time_local = '11/08/17 1925',
            print_time_gmt = '11/09/17 0025',
            weights = [
                dict(name='OEW', weight='127496', forward=None,
                     cg_percent_mac='24.12', aft=None),
                dict(name='Zero Fuel', weight='148752', forward='10.17',
                     cg_percent_mac='22.53', aft='35.77'),
                dict(name='Takeoff', weight='178352', forward='10',
                     cg_percent_mac='26.81', aft='36.9'),
                dict(name='Taxi', weight='179352', forward='9.99',
                     cg_percent_mac='26.66', aft='36.91'),
                dict(name='Landing', weight='165800', forward='10.08',
                     cg_percent_mac='23.83', aft='36.74'),
                dict(name='Fuel Wing Wt', weight='29526'),
                dict(name='Fuel Center Wt', weight='74'),
                dict(name='Ramp Fuel Wt', weight='30600'),
                dict(name='Taxi Fuel Wt', weight='1000'),
                dict(name='Takeoff Fuel', weight='29600'),
                dict(name='PLAN FUEL BURN', weight='12552'),
            ],
            aircraft_configurations = [
                dict(name='Cargo Wt', value='17986'),
                dict(name='Main Deck Wt', value='13395'),
                dict(name='Belly Wt', value='4591'),
                dict(name='Revenue Wt', value='12340'),
                dict(name='Fwd ACM/FA 1/1', value='240/210'),
                dict(name='Aft ACM/FA/PAX 1/2/12', value='240/420/2160'),
            ],
            positions = [
                dict(position='B1', unit_load_device=None,
                     destination_icao=None, destination_iata=None, weight=None,
                     weight_unit=None, building=None),
                dict(position='B2', unit_load_device=None,
                     destination_icao=None,destination_iata=None, weight=None,
                     weight_unit=None, building=None),
                dict(position='B3', unit_load_device=None,
                     destination_icao=None, destination_iata=None, weight=None,
                     weight_unit=None, building=None),
                dict(position='B4', unit_load_device='463L',
                     destination_icao='KNGU', destination_iata=None,
                     weight='1635', weight_unit='LB', building='C'),
                dict(position='B5', unit_load_device='463L',
                     destination_icao='KNGU', destination_iata=None,
                     weight='1970', weight_unit='LB', building='C'),
                dict(position='B6', unit_load_device='463L',
                     destination_icao='KNGU', destination_iata=None,
                     weight='3115', weight_unit='LB', building='C'),
                dict(position='B7', unit_load_device='463L',
                     destination_icao='KNGU', destination_iata=None,
                     weight='3190', weight_unit='LB', building='C'),
                dict(position='B8', unit_load_device='463L',
                     destination_icao='KNGU', destination_iata=None,
                     weight='3485', weight_unit='LB', building='C'),
                dict(position='B9', unit_load_device=None,
                     destination_icao=None, destination_iata=None, weight=None,
                     weight_unit=None, building=None),
                dict(position='B10', unit_load_device=None,
                     destination_icao=None, destination_iata=None, weight=None,
                     weight_unit=None, building=None),
                dict(position='PAX1', unit_load_device=None,
                     destination_icao=None, destination_iata=None,
                     weight='2400', weight_unit='LB', building='C'),
                dict(position='1', unit_load_device='CREW BAGS',
                     destination_icao=None, destination_iata=None,
                     weight='250', weight_unit='LB', building='C'),
                dict(position='2', unit_load_device='PAX BAGS',
                     destination_icao=None, destination_iata=None,
                     weight='720', weight_unit='LB', building='C'),
                dict(position='3', unit_load_device='FAK',
                     destination_icao=None, destination_iata=None,
                     weight='2249', weight_unit='LB', building='C'),
                dict(position='4', unit_load_device='FAK',
                     destination_icao=None, destination_iata=None,
                     weight='1372', weight_unit='LB', building='C'),
            ]
        )
        with open('tests/pistol_message.txt') as pistol_message_file:
            text = pistol_message_file.read()
            actual = parse.loadplan_from_text(text)
            self.maxDiff = None
            self.assertDictEqual(actual, expect)

    def test_parse_position(self):
        # dot nill
        self.assertDictEqual(parse._position('-A1.NIL'),
                             dict(position = 'A1',
                                  unit_load_device = None,
                                  destination_icao = None,
                                  destination_iata = None,
                                  weight = None,
                                  weight_unit = None,
                                  building = None))
        # normal expected
        self.assertDictEqual(parse._position('-A2L/AAA00000AA/NGU/200LB/A'),
                             dict(position = 'A2L',
                                  unit_load_device = 'AAA00000AA',
                                  destination_iata = 'NGU',
                                  destination_icao = None,
                                  weight = '200',
                                  weight_unit = 'LB',
                                  building = 'A'))
        # allow missing and strip whitespace
        self.assertDictEqual(parse._position('-A3L/CCC00000CC/ /300LB/B'),
                             dict(position = 'A3L',
                                  unit_load_device = 'CCC00000CC',
                                  destination_icao = None,
                                  destination_iata = None,
                                  weight = '300',
                                  weight_unit = 'LB',
                                  building = 'B'))
        # enforce format: does not start with dash
        with self.assertRaises(parse.ParsingError):
            parse._position('A4/DDD00000DD/ /200LB/A')
        # enforce format: must not contain newlines
        with self.assertRaises(parse.ParsingError):
            parse._position('-A5/EEE00000EE/FFF/200LB/A\n-A6/FFF00000FF/GGG/201LB/A')
        # enforce weight units: must be LB or KG
        with self.assertRaises(parse.ParsingError):
            parse._position('-A5/HHH00000HH/ /123__/A')

    def test_parse__flight_number_and_company(self):
        # function parses string and return flight number and company tuple
        self.assertEqual(parse._flight_number_and_company('AAA1234'), ('1234', 'AAA'))
        self.assertEqual(parse._flight_number_and_company('AAA100'), ('100', 'AAA'))
        # this is the current behavior, almost certainely not desired.
        self.assertEqual(parse._flight_number_and_company('ATIATN100'), ('100', 'ATI'))


if __name__ == '__main__':
    unittest.main()
