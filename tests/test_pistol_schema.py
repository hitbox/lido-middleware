import unittest

from datetime import datetime

from pistol.parse import loadplan_from_text
from pistol.schema import LoadPlanSchema

class TestLoadPlan(unittest.TestCase):

    def test_loadplan_from_text(self):
        """
        Test loadplan object from text
        """
        with open('tests/pistol_message.txt') as pistol_message_file:
            text = pistol_message_file.read()
            loadplandata = loadplan_from_text(text)
            loadplan = LoadPlanSchema().load(loadplandata)
        self.assertEqual(loadplan['load_planner'], 'LPNAME<lpname@company.com>')
        self.assertEqual(loadplan['company'], 'COM')
        self.assertEqual(loadplan['flight_number'], '123')
        self.assertEqual(loadplan['aircraft_registration'], 'N000ZZ')
        self.assertEqual(loadplan['origin_icao'], 'KMIA')
        self.assertEqual(loadplan['actual_departure_time'], None)
        self.assertEqual(loadplan['color_code'], 'B PURPLE')
        self.assertEqual(loadplan['all_weights_unit'], 'LB')
        self.assertEqual(loadplan['computer'], 'COMPUTER1')
        self.assertEqual(loadplan['pistol_version'], 'PSTL_1900.01.01.0001')
        self.assertEqual(loadplan['print_time_gmt'], datetime(2017, 11, 9, 0, 25))
        self.assertEqual(loadplan['print_time_local'], datetime(2017, 11, 8, 19, 25))

        a = loadplan['positions']
        b = [
            dict(position='B1', unit_load_device=None, destination_icao=None,
                 weight=None, weight_unit=None, building=None),
            dict(position='B2', unit_load_device=None, destination_icao=None,
                 weight=None, weight_unit=None, building=None),
            dict(position='B3', unit_load_device=None, destination_icao=None,
                 weight=None, weight_unit=None, building=None),
            dict(position='B4', unit_load_device='463L',
                 destination_icao='KNGU', destination_iata='NGU', weight=1635,
                 weight_unit='LB', building='C'),
            dict(position='B5', unit_load_device='463L',
                 destination_icao='KNGU', destination_iata='NGU', weight=1970,
                 weight_unit='LB', building='C'),
            dict(position='B6', unit_load_device='463L',
                 destination_icao='KNGU', destination_iata='NGU', weight=3115,
                 weight_unit='LB', building='C'),
            dict(position='B7', unit_load_device='463L',
                 destination_icao='KNGU', destination_iata='NGU', weight=3190,
                 weight_unit='LB', building='C'),
            dict(position='B8', unit_load_device='463L',
                 destination_icao='KNGU', destination_iata='NGU', weight=3485,
                 weight_unit='LB', building='C'),
            dict(position='B9', unit_load_device=None, destination_icao=None,
                 weight=None, weight_unit=None, building=None),
            dict(position='B10', unit_load_device=None, destination_icao=None,
                 weight=None, weight_unit=None, building=None),
            dict(position='PAX1', unit_load_device=None, destination_icao=None,
                 weight=2400, weight_unit='LB', building='C'),
            dict(position='1', unit_load_device='CREW BAGS',
                 destination_icao=None, weight=250, weight_unit='LB',
                 building='C'),
            dict(position='2', unit_load_device='PAX BAGS',
                 destination_icao=None, weight=720, weight_unit='LB',
                 building='C'),
            dict(position='3', unit_load_device='FAK', destination_icao=None,
                 weight=2249, weight_unit='LB', building='C'),
            dict(position='4', unit_load_device='FAK', destination_icao=None,
                 weight=1372, weight_unit='LB', building='C'),
        ]
        self.assertListEqual(a, b)

        a = loadplan['weights']
        b = [
            dict(name='OEW', weight=127496, cg_percent_mac=24.12, forward=None, aft=None),
            dict(name='Zero Fuel', weight=148752, forward=10.17, cg_percent_mac=22.53, aft=35.77),
            dict(name='Takeoff', weight=178352, forward=10.0, cg_percent_mac=26.81, aft=36.9),
            dict(name='Taxi', weight=179352, forward=9.99, cg_percent_mac=26.66, aft=36.91),
            dict(name='Landing', weight=165800, forward=10.08, cg_percent_mac=23.83, aft=36.74),
            dict(name='Fuel Wing Wt', weight=29526),
            dict(name='Fuel Center Wt', weight=74),
            dict(name='Ramp Fuel Wt', weight=30600),
            dict(name='Taxi Fuel Wt', weight=1000),
            dict(name='Takeoff Fuel', weight=29600),
            dict(name='PLAN FUEL BURN', weight=12552),
        ]
        self.assertListEqual(a, b)

        a = loadplan['aircraft_configurations']
        b = [
            dict(name='Cargo Wt', value='17986'),
            dict(name='Main Deck Wt', value='13395'),
            dict(name='Belly Wt', value='4591'),
            dict(name='Revenue Wt', value='12340'),
            dict(name='Fwd ACM/FA 1/1', value='240/210'),
            dict(name='Aft ACM/FA/PAX 1/2/12', value='240/420/2160'),
        ]
        self.assertListEqual(a, b)
