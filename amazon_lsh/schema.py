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

from extradata import airline_designators
from schema import CommonSchemaMixin
from schema import PRINT_DATETIME_FORMAT
from units import VALID_WEIGHT_UNITS

class PositionSchema(Schema):

    position = String(allow_none=True)
    weight = Integer()


class LoadPlanSchema(CommonSchemaMixin, Schema):

    @pre_load
    def pre_load(self, data, **kwargs):
        # the company or airline designator appears at the beginning of this string.
        if data['airline_and_flight_number'] != data['airline_and_flight_number2']:
            raise ValidationError('Flight number do not match')
        company_or_airline_and_flight_number = data['airline_and_flight_number']
        data.update(
            airline_designators.split_company_or_airline_and_flight_number(
                company_or_airline_and_flight_number))
        del data['airline_and_flight_number']
        del data['airline_and_flight_number2']

        if data['aircraft_registration'] != data['aircraft_registration2']:
            raise ValidationError('Aircraft registrations do not match')
        del data['aircraft_registration2']

        # unnest
        data['actual_takeoff_fuel'] = data['TO FUEL']['weight_kg']
        data['actual_zero_fuel_weight'] = data['ZFW ACT']['weight_kg']
        del data['LAW ACT']
        del data['TO FUEL']
        del data['TOW ACT']
        del data['TRIP FUEL']
        del data['ZFW ACT']
        del data['loadsheet_final_number']
        del data['unknown1']
        del data['unknown2']
        del data['unknown3']

        return data

    aircraft_registration = String()
    airline_designator = String(allow_none=True, required=True, validate=Length(max=3))
    all_weights_unit = Constant('KG')
    company = String(allow_none=True, required=True)
    day = Integer(required=True)
    flight_number = String(required=True)
    print_time_gmt = DateTime(data_key='date', format='%d%b%y')
    uload = Integer()

    # CommonSchemaMixin override
    dry_operating_index = Float(data_key='DOI')

    destination_iata = String(required=True, validate=Length(max=3))
    origin_iata = String(required=True, validate=Length(max=3))

    positions = List(Nested(PositionSchema))

    actual_takeoff_fuel = Integer(required=True)
    actual_zero_fuel_weight = Integer(required=True)
    center_of_gravity = Float(data_key='MACZFW', required=True)
    dry_operating_weight = Integer(data_key='DOW', required=True)

    # post_load:
    cargo_weight = Integer()

    # unused
    bi = Float(data_key='BI')
    bw = Float(data_key='BW')
    lilaw = Float(data_key='LILAW')
    litow = Float(data_key='LITOW')
    lizfw = Float(data_key='LIZFW')
    maclaw = Float(data_key='MACLAW')
    mactow = Float(data_key='MACTOW')

    @post_load
    def post_load(self, data, **kwargs):
        """
        Validate fields.
        """
        if not (data.get('company') or data.get('airline_designator')):
            raise ValidationError('company or airline_designator must exist')
        data['cargo_weight'] = sum(item['weight'] for item in data['positions'])
        return data
