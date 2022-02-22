import unittest

from marshmallow import Schema
from marshmallow import ValidationError

from schema import CommonSchemaMixin
from schema import dict_for_company_and_flight_number
from schema import dict_for_flight_number
from schema import mid_digits

class TestCommonSchemaMixin(unittest.TestCase):
    """
    Test the common schema mixin that provides constants for Lido messages.
    """

    def setUp(self):
        class TestSchema(CommonSchemaMixin, Schema):
            pass
        self.schema = TestSchema()

    def test_common_schema_mixin_load(self):
        # constants common to lido messages
        result = self.schema.load(dict())
        self.assertEqual(result,
            dict(
                planning_status = '04',
                duplicate_number = '1',
                revision_number = '00',
                operational_suffix = ' ',
                pax_baggage_indicator = 'Y',
                cargo_mail_indicator = 'Y',
                transit_load_indicator = 'Y',
                tail_tank_indicator = ' ',
                estimated_pax = 0,
                dry_operating_index = None,
                estimated_pax_class_one = None,
                estimated_pax_class_two = None,
                estimated_pax_class_three = None,
            ))


class TestDictForCompanyAndFlightNumber(unittest.TestCase):
    """
    Test function that gathers data from the dense "company and flight number
    and other data" line.
    """

    def test_dict_for_company_and_flight_number(self):
        # NOTE:
        # has to be real company code because these are looked up. should have
        # made this configurable and the data source in a private, untracked,
        # file.
        self.assertEqual(
            dict_for_company_and_flight_number('ABX1234'),
            dict(
                airline_designator = 'GB',
                company = 'ABX',
                flight_number = '1234',
            ))
        with self.assertRaises(ValidationError):
            self.assertEqual(
                dict_for_company_and_flight_number('NAC1234'),
                dict(
                    airline_designator = '',
                    company = '',
                    flight_number = '',
                ))


class TestDictForFlightNumber(unittest.TestCase):
    """
    Test func returning dict for flight number and optionally operational
    suffix. This is used specifically in sable.schema.
    """

    def test_dict_for_flight_number(self):
        # basically just testing mid_digits again
        # this bypasses the company parsing
        self.assertEqual(dict_for_flight_number('ABX9999'), dict(flight_number='9999'))
        self.assertEqual(dict_for_flight_number('ABXABX9999'), dict(flight_number='9999'))
        self.assertEqual(dict_for_flight_number('GB9999'), dict(flight_number='9999'))
        #
        self.assertEqual(
            dict_for_flight_number('GB9999Z'),
            dict(flight_number='9999', operational_suffix='Z'))


class TestMidDigits(unittest.TestCase):
    """
    Test the "digits in between" flight number processor.
    """

    def test_mid_digits_empty(self):
        self.assertEqual(mid_digits(''), '')

    def test_mid_digits_onlydigits(self):
        self.assertEqual(mid_digits('123'), '123')
        self.assertEqual(mid_digits('012'), '12')
        self.assertEqual(mid_digits('120'), '120')

    def test_mid_digits_onlyalpha(self):
        self.assertEqual(mid_digits('abc'), '')

    def test_mid_digits_mixed(self):
        self.assertEqual(mid_digits('abc123'), '123')
        self.assertEqual(mid_digits('abc012'), '12')
        self.assertEqual(mid_digits('abc120'), '120')
        self.assertEqual(mid_digits('abc000'), '')
        #
        self.assertEqual(mid_digits('123def'), '123')
        self.assertEqual(mid_digits('012def'), '12')
        self.assertEqual(mid_digits('120def'), '120')
        self.assertEqual(mid_digits('000def'), '')
        #
        self.assertEqual(mid_digits('abc123def'), '123')
        self.assertEqual(mid_digits('abc012def'), '12')
        self.assertEqual(mid_digits('abc120def'), '120')
        self.assertEqual(mid_digits('abc010def'), '10')
        self.assertEqual(mid_digits('abc000def'), '')

    def test_mid_digits_trailing_digits(self):
        # additional problem to be solved of digits after alpha chars on end
        self.assertEqual(mid_digits('123def01'), '123')
        self.assertEqual(mid_digits('012def01'), '12')
        self.assertEqual(mid_digits('120def01'), '120')
        self.assertEqual(mid_digits('000def01'), '')
        #
        self.assertEqual(mid_digits('abc123def123'), '123')
        self.assertEqual(mid_digits('abc012def123'), '12')
        self.assertEqual(mid_digits('abc120def123'), '120')
        self.assertEqual(mid_digits('abc010def123'), '10')
        self.assertEqual(mid_digits('abc000def123'), '')


if __name__ == '__main__':
    unittest.main()
