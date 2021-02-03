import unittest

from extradata import ExtradataError
from extradata import aircraftregistration
from extradata import airline_designators
from extradata import stations

class TestAircraftRegistrationAirlineMapping(unittest.TestCase):

    @unittest.skip('mapping will come from netline/base database')
    def test_airline(self):
        pass


class TestAirlineDesignators(unittest.TestCase):

    def test_by_company(self):
        self.assertEqual(airline_designators.by_company['ABX'], 'GB')

    def test_by_airline(self):
        self.assertEqual(airline_designators.by_airline['GB'], 'ABX')

    def test_split_company_or_airline_and_flight_number(self):
        _f = airline_designators.split_company_or_airline_and_flight_number
        # company -> code
        self.assertEqual(
            _f('ABX1234'),
            {'company': 'ABX', 'airline_designator': 'GB', 'flight_number': '1234'})
        # code -> company
        self.assertEqual(
            _f('GB1234'),
            {'company': 'ABX', 'airline_designator': 'GB', 'flight_number': '1234'})
        # not exists
        with self.assertRaises(ExtradataError):
            self.assertEqual(
                _f('NOPE1234'),
                {'company': 'ABX', 'airline_designator': 'GB', 'flight_number': '1234'})


class TestStations(unittest.TestCase):

    def test_detect_code_type(self):
        self.assertEqual(stations.detect_code_type('KNGU'), 'icao')
        self.assertEqual(stations.detect_code_type('NGU'), 'iata')
        #
        with self.assertRaises(ExtradataError):
            stations.detect_code_type('NOPE')

    def test_filled(self):
        self.assertEqual(stations.filled('NGU'), {'iata': 'NGU', 'icao': 'KNGU'})
        self.assertEqual(stations.filled('KNGU'), {'iata': 'NGU', 'icao': 'KNGU'})


if __name__ == '__main__':
    unittest.main()
