import unittest

from extradata import ExtradataError
from extradata import airline_designators
from extradata import stations

class TestAirlineDesignators(unittest.TestCase):
    """
    AirlineDesignators tests
    """

    def test_by_company(self):
        self.assertEqual(airline_designators.by_company['ABX'], 'GB')
        self.assertEqual(airline_designators.by_company['AMZ'], None)

    def test_by_airline(self):
        self.assertEqual(airline_designators.by_airline['GB'], 'ABX')

    def test_split_company_or_airline_and_flight_number(self):
        # shorten name
        stringsplit = airline_designators.split_company_or_airline_and_flight_number
        # company -> airline code
        a = stringsplit('ABX1234')
        b = {'company': 'ABX', 'airline_designator': 'GB', 'flight_number': '1234'}
        self.assertEqual(a, b)
        # airline code -> company
        a = stringsplit('GB1234')
        b = {'company': 'ABX', 'airline_designator': 'GB', 'flight_number': '1234'}
        self.assertEqual(a, b)
        # AMZ -> None
        a = stringsplit('AMZ8888')
        b = {'company': 'AMZ', 'airline_designator': None, 'flight_number': '8888'}
        self.assertEqual(a, b)
        # not exists
        with self.assertRaises(ExtradataError):
            a = stringsplit('NOPE1234')
            b = {'company': 'ABX', 'airline_designator': 'GB', 'flight_number': '1234'}
            self.assertEqual(a, b)


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
