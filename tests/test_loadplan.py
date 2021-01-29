import unittest

from datetime import datetime

from loadplan import AircraftConfig
from loadplan import LoadPlan
from loadplan import Position
from loadplan import Weight
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
        self.assertEqual(loadplan.load_planner, 'LPNAME<lpname@company.com>')
        self.assertEqual(loadplan.company, 'COM')
        self.assertEqual(loadplan.flight_number, '123')
        self.assertEqual(loadplan.aircraft_registration, 'N000ZZ')
        self.assertEqual(loadplan.origin_station, 'KMIA')
        self.assertEqual(loadplan.actual_departure_time, None)
        self.assertEqual(loadplan.color_code, 'B PURPLE')
        self.assertEqual(loadplan.all_weights_unit, 'LB')
        self.assertEqual(loadplan.computer, 'COMPUTER1')
        self.assertEqual(loadplan.pistol_version, 'PSTL_1900.01.01.0001')
        self.assertEqual(loadplan.print_time_gmt, datetime(2017, 11, 9, 0, 25))
        self.assertEqual(loadplan.print_time_local, datetime(2017, 11, 8, 19, 25))

        a = loadplan.positions
        b = [
            Position(position='B1', unit_load_device=None, destination=None,
                     weight=None, weight_unit=None, building=None),
            Position(position='B2', unit_load_device=None, destination=None,
                     weight=None, weight_unit=None, building=None),
            Position(position='B3', unit_load_device=None, destination=None,
                     weight=None, weight_unit=None, building=None),
            Position(position='B4', unit_load_device='463L',
                     destination='KNGU', weight=1635, weight_unit='LB',
                     building='C'),
            Position(position='B5', unit_load_device='463L',
                     destination='KNGU', weight=1970, weight_unit='LB',
                     building='C'),
            Position(position='B6', unit_load_device='463L',
                     destination='KNGU', weight=3115, weight_unit='LB',
                     building='C'),
            Position(position='B7', unit_load_device='463L',
                     destination='KNGU', weight=3190, weight_unit='LB',
                     building='C'),
            Position(position='B8', unit_load_device='463L',
                     destination='KNGU', weight=3485, weight_unit='LB',
                     building='C'),
            Position(position='B9', unit_load_device=None, destination=None,
                     weight=None, weight_unit=None, building=None),
            Position(position='B10', unit_load_device=None, destination=None,
                     weight=None, weight_unit=None, building=None),
            Position(position='PAX1', unit_load_device=None, destination=None,
                     weight=2400, weight_unit='LB', building='C'),
            Position(position='1', unit_load_device='CREW BAGS',
                     destination=None, weight=250, weight_unit='LB',
                     building='C'),
            Position(position='2', unit_load_device='PAX BAGS',
                     destination=None, weight=720, weight_unit='LB',
                     building='C'),
            Position(position='3', unit_load_device='FAK', destination=None,
                     weight=2249, weight_unit='LB', building='C'),
            Position(position='4', unit_load_device='FAK', destination=None,
                     weight=1372, weight_unit='LB', building='C'),
        ]
        self.assertListEqual(a, b)

        a = loadplan.weights
        b = [
            Weight(name='OEW', weight=127496, cg_percent_mac=24.12),
            Weight(name='Zero Fuel', weight=148752, forward=10.17, cg_percent_mac=22.53, aft=35.77),
            Weight(name='Takeoff', weight=178352, forward=10.0, cg_percent_mac=26.81, aft=36.9),
            Weight(name='Taxi', weight=179352, forward=9.99, cg_percent_mac=26.66, aft=36.91),
            Weight(name='Landing', weight=165800, forward=10.08, cg_percent_mac=23.83, aft=36.74),
            Weight(name='Fuel Wing Wt', weight=29526),
            Weight(name='Fuel Center Wt', weight=74),
            Weight(name='Ramp Fuel Wt', weight=30600),
            Weight(name='Taxi Fuel Wt', weight=1000),
            Weight(name='Takeoff Fuel', weight=29600),
            Weight(name='PLAN FUEL BURN', weight=12552),
        ]
        self.assertListEqual(a, b)

        a = loadplan.aircraft_configurations
        b = [
            AircraftConfig(name='Cargo Wt', value='17986'),
            AircraftConfig(name='Main Deck Wt', value='13395'),
            AircraftConfig(name='Belly Wt', value='4591'),
            AircraftConfig(name='Revenue Wt', value='12340'),
            AircraftConfig(name='Fwd ACM/FA 1/1', value='240/210'),
            AircraftConfig(name='Aft ACM/FA/PAX 1/2/12', value='240/420/2160'),
        ]
        self.assertListEqual(a, b)
