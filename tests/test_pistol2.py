import json
import os
import pickle
import unittest

from pistol2 import extract

class TextExtract(unittest.TestCase):

    def test_text_extract1(self):
        expect = {
            'ad_unknown1': '0113',
            'ad_unknown2': '0128',
            'aircraft_configurations': [
                {'name': 'Cargo Wt', 'value': '8218'},
                {'name': 'Main Deck Wt', 'value': '3204'},
                {'name': 'Belly Wt', 'value': '5014'},
                {'name': 'Revenue Wt', 'value': '3067'},
                {'name': 'Fwd ACM/FA 1/1', 'value': '289/219'},
                {'name': 'Aft ACM/FA/PAX 0/1/22', 'value': '0/219/3921'},
            ],
            'aircraft_registration1': 'N753CX',
            'aircraft_registration2': 'N753CX',
            'all_weights_unit': 'LB',
            'color_code': 'B WHITE',
            'company_and_flight_number1': 'ATIATN731',
            'company_and_flight_number2': 'ATIATN731',
            'computer': 'ACER',
            'day1': '01',
            'day2': '01',
            'destination_iata_or_icao': 'OKO',
            'load_planner': 'john.doe<john.doe@company.com>',
            'origin_iata_or_icao': 'QPG',
            'payload': '12139',
            'pistol_version': 'PSTL_2022.02.07.1923',
            'print_time_gmt': '08/01/23 0130',
            'print_time_local': '08/01/23 0930',
            'souls_onboard': '27',
            'uld_count': '3',
            'weights': [
                {
                    'aft': 'N/A',
                    'cg_percent_mac': '21.06',
                    'forward': 'N/A',
                    'name': 'OEW',
                    'weight': '128730',
                },
                {
                    'aft': '35.11',
                    'cg_percent_mac': '28.48',
                    'forward': '11.19',
                    'name': 'Zero Fuel',
                    'weight': '141596'},
                {
                    'aft': '37.99',
                    'cg_percent_mac': '24.32',
                    'forward': '11',
                    'name': 'Takeoff',
                    'weight': '213996',
                },
                {
                    'aft': '38.01',
                    'cg_percent_mac': '24.26',
                    'forward': '11.15',
                    'name': 'Taxi',
                    'weight': '215596',
                },
                {
                    'aft': '37.53',
                    'cg_percent_mac': '29.25',
                    'forward': '11.1',
                    'name': 'Landing',
                    'weight': '159615',
                },
                {'name': 'Fuel Wing Wt', 'weight': '29158'},
                {'name': 'Fuel Center Wt', 'weight': '43242'},
                {'name': 'Ramp Fuel Wt', 'weight': '74000'},
                {'name': 'Taxi Fuel Wt', 'weight': '1600'},
                {'name': 'Takeoff Fuel', 'weight': '72400'},
                {'name': 'PLAN FUEL BURN', 'weight': '54381'},
            ],
        }
        with open('tests/data/pistol_extract1.json') as json_file:
            message = json.load(json_file)
            self.assertTrue(message)
            data = extract.loadplan_from_text(message['body'])
            self.assertEqual(data, expect)

    def test_with_fuel_ballast(self):
        expect = {
            'ad_unknown1': 'Update',
            'ad_unknown2': 'Update',
            'aircraft_configurations': [
                {'name': 'Cargo Wt', 'value': '0'},
                {'name': 'Main Deck Wt', 'value': '0'},
                {'name': 'Belly Wt', 'value': '0'},
                {'name': 'Revenue Wt', 'value': '0'},
                {'name': 'ACM    0', 'value': '0'},
            ],
            'aircraft_registration1': 'N750AX',
            'aircraft_registration2': 'N750AX',
            'all_weights_unit': 'LB',
            'color_code': 'A Green',
            'company_and_flight_number1': 'ABX36',
            'company_and_flight_number2': 'ABX36',
            'computer': 'ATSG20132',
            'day1': '09',
            'day2': '09',
            'destination_iata_or_icao': 'ILN',
            'load_planner': 'JANE DOE<jane.doe@company.com>',
            'origin_iata_or_icao': 'GSO',
            'payload': '0',
            'pistol_version': 'PSTL_2022.02.07.1923',
            'print_time_gmt': '08/09/23 2056',
            'print_time_local': '08/09/23 1656',
            'souls_onboard': '2',
            'uld_count': '0',
            'weights': [
                {
                    'aft': 'N/A',
                    'cg_percent_mac': '15.38',
                    'forward': 'N/A',
                    'name': 'OEW',
                    'weight': '167760',
                },
                {
                    'aft': '28.92',
                    'cg_percent_mac': '15.36',
                    'forward': '12.95',
                    'name': 'Zero Fuel',
                    'weight': '168000',
                },
                {
                    'aft': '35.33',
                    'cg_percent_mac': '16.93',
                    'forward': '11.7',
                    'name': 'Takeoff',
                    'weight': '222320',
                },
                {
                    'aft': '35.36',
                    'cg_percent_mac': '17',
                    'forward': '11.7',
                    'name': 'Taxi',
                    'weight': '222760',
                },
                {
                    'aft': '32.98',
                    'cg_percent_mac': '15.01',
                    'forward': '11.78',
                    'name': 'Landing',
                    'weight': '200986',
                },
                # NOTE
                # - left off without implementing fuel ballast from
                #   the "Fuel Wing Wt" line
                # - think the problem is in xml plucking in central_load_plan
                #{'name': 'fuel_ballast', 'weight': '240'},
                {'name': 'Fuel Wing Wt', 'weight': '54560'},
                {'name': 'Fuel Center Wt', 'weight': '0'},
                {'name': 'Ramp Fuel Wt', 'weight': '55000'},
                {'name': 'Taxi Fuel Wt', 'weight': '440'},
                {'name': 'Takeoff Fuel', 'weight': '54560'},
                {'name': 'EST FUEL BURN', 'weight': '21334'},
            ]
        }
        with open('tests/data/pistol_with_fuel_ballast.json') as json_file:
            message = json.load(json_file)
            self.assertTrue(message)
            data = extract.loadplan_from_text(message['body'])
            self.assertEqual(data, expect)


if __name__ == '__main__':
    unittest.main()
