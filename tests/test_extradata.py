import unittest

from extradata import ExtradataError
from extradata import stations

class TestExtradata(unittest.TestCase):

    def test_stations_detect_code_type(self):
        self.assertEqual(stations.detect_code_type('KNGU'), 'icao')
        self.assertEqual(stations.detect_code_type('NGU'), 'iata')
        #
        with self.assertRaises(ExtradataError):
            stations.detect_code_type('NOPE')

    def test_stations_update_other_station_by_type(self):
        # sets icao
        d = dict(destination_iata='NGU', destination_icao=None)
        stations.update_other_station_by_type(d, 'destination')
        self.assertEqual(d, dict(destination_iata='NGU', destination_icao='KNGU'))
        # sets iata
        d = dict(destination_iata=None, destination_icao='KNGU')
        stations.update_other_station_by_type(d, 'destination')
        self.assertEqual(d, dict(destination_iata='NGU', destination_icao='KNGU'))
        # raise for key not exist
        with self.assertRaises(KeyError):
            stations.update_other_station_by_type(dict(), 'destination')
        # raise for both set
        with self.assertRaises(ExtradataError):
            stations.update_other_station_by_type(
                dict(destination_iata='NGU', destination_icao='KNGU'),
                'destination')


if __name__ == '__main__':
    unittest.main()
