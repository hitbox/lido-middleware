import unittest

from datetime import datetime

from wsiweather import parse

class TestParseTAFFilename(unittest.TestCase):

    def test_parse_filename(self):
        self.assertEqual(
            parse.taf_filename('320.11130.20210330T094819.1617088897'),
            (None, None, datetime(2021, 3, 30, 9, 48, 19), None)
        )
        self.assertEqual(
            parse.taf_filename('320.3405.20210401T081143.1616068587'),
            (None, None, datetime(2021, 4, 1, 8, 11, 43), None)
        )
        self.assertEqual(
            parse.taf_filename('320.3405.20210401T100810.1616070147'),
            (None, None, datetime(2021, 4, 1, 10, 8, 10), None)
        )
        self.assertEqual(
            parse.taf_filename('320.5633.20210405T180303.1617184099'),
            (None, None, datetime(2021, 4, 5, 18, 3, 3), None)
        )
        self.assertEqual(
            parse.taf_filename('320.6662.20210328T051644.1616008687'),
            (None, None, datetime(2021, 3, 28, 5, 16, 44), None)
        )
        self.assertEqual(
            parse.taf_filename('320.9345.20210329T133735.1616028649'),
            (None, None, datetime(2021, 3, 29, 13, 37, 35), None)
        )
        self.assertEqual(
            parse.taf_filename('320.9345.20210331T014957.1616049100'),
            (None, None, datetime(2021, 3, 31, 1, 49, 57), None)
        )


if __name__ == '__main__':
    unittest.main()
