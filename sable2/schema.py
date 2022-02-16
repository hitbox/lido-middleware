import string

from marshmallow import Schema
from marshmallow import post_load
from marshmallow import pre_load
from marshmallow.exceptions import ValidationError
from marshmallow.fields import Constant
from marshmallow.fields import DateTime
from marshmallow.fields import Float
from marshmallow.fields import Integer
from marshmallow.fields import List
from marshmallow.fields import Nested
from marshmallow.fields import String
from marshmallow.validate import Length
from marshmallow.validate import OneOf

from extradata import ExtradataError
from extradata import airline_designators
from extradata import airline_map
from schema import CommonSchemaMixin
from schema import PRINT_DATETIME_FORMAT
from units import VALID_WEIGHT_UNITS

class Position(Schema):

    position = String(data_key='POS')
    destination = String(data_key='DST')
    uldnumber = String(data_key='ULDNUMBER')
    tare = Integer(data_key='TARE')
    nett = Integer(data_key='NETT')
    total = Integer(data_key='TOTAL')
    flag = String(data_key='FLAG')
    vol = Integer(data_key='VOL')


class LoadPlanSchema(CommonSchemaMixin, Schema):
    """
    Sable Load Plan Schema using LDM (planning status 05).
    """

    @pre_load
    def pre_load(self, data, **kwargs):
        # the company or airline designator appears at the beginning of this string.
        company_or_airline_and_flight_number = data['airline_and_flight_number']

        airline_company = airline_designators.split_company_or_airline_and_flight_number(
                company_or_airline_and_flight_number)

        # resolve AMZ (Amazon) using email to addresses
        if airline_company['company'] == 'AMZ':
            company = airline_map.from_toaddresses(data['message_to'])
            airline_company['airline_designator'] = company
        del data['message_to']

        data.update(airline_company)
        del data['airline_and_flight_number']

        if data['flight_number'] and data['flight_number'][-1] in string.ascii_uppercase:
            # optional operational_suffix is present at end of flight_number,
            # strip it off and put it where it belongs
            data['operational_suffix'] = data['flight_number'][-1]
            data['flight_number'] = data['flight_number'][:-1]

        data['cargo_weight'] = data['net_weight']

        # uld count
        if 'uld_count' not in data:
            data['uld_count'] = sum(1 for row in data['positions']
                                    if row['ULDNUMBER'].lower() not in ('void', 'loose'))

        return data

    planning_status = Constant('55', validate=Length(max=2))

    payload = Integer()
    flight_number = String(required=True)
    company = String(required=True)
    airline_designator = String(required=True, validate=Length(max=3))
    day = Integer(required=True)
    tail = String()
    origin_iata = String(required=True, validate=Length(max=3))
    destination_iata = String(required=True, validate=Length(max=3))
    operational_suffix = String(missing='', validate=OneOf(string.ascii_uppercase))

    net_weight = Integer()
    uld_count = Integer()
    cargo_weight = Integer()

    uload = Integer()
    souls_onboard = Integer()
    all_weights_unit = String(
        data_key = 'weights_unit',
        required = True,
        validate = OneOf(VALID_WEIGHT_UNITS))
    print_time_gmt = DateTime(data_key='message_date', format=PRINT_DATETIME_FORMAT)
    message_from = String()

    actual_takeoff_fuel = Integer(missing=0)
    actual_zero_fuel_weight = Integer(missing=0)
    center_of_gravity = Float(data_key='cg_percent_mac', missing=None)
    dry_operating_weight = Integer(missing=None)
    revenue_weight = Integer()
    positions = List(Nested(Position))

    gross_weight = Integer(data_key='gross')

    @post_load
    def post_load(self, data, **kwargs):

        # estimated total traffic load calculation
        if data['souls_onboard'] > 1:
            # what is ACM?
            acm = data['souls_onboard'] - 2
        else:
            acm = 0
        data['estimated_total_traffic_load'] = data['gross_weight'] + (acm * 220)

        fac = 2.20462
        if data['all_weights_unit'] in ('LB', '#'):
            data['gross_weight_kg'] = data['gross_weight'] / fac
            data['net_weight_kg'] = data['net_weight'] / fac
        else:
            data['gross_weight_kg'] = float(data['gross_weight'])
            data['net_weight_kg'] = float(data['net_weight'])

        return data
