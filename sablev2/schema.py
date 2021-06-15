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

class LoadPlanSchema(CommonSchemaMixin, Schema):
    """
    Sable Load Plan Schema using LDM (planning status 05).
    """

    @pre_load
    def pre_load(self, data, **kwargs):
        # the company or airline designator appears at the beginning of this string.
        company_or_airline_and_flight_number = data['airline_and_flight_number']
        data.update(
            airline_designators.split_company_or_airline_and_flight_number(
                company_or_airline_and_flight_number))
        del data['airline_and_flight_number']

        return data

    planning_status = Constant('05', validate=Length(max=2))

    flight_number = String(required=True)
    company = String(allow_none=True, required=True)
    airline_designator = String(allow_none=True, required=True, validate=Length(max=3))
    day = Integer(required=True)
    tail = String()
    origin_iata = String(required=True, validate=Length(max=3))
    destination_iata = String(required=True, validate=Length(max=3))

    net_weight = Integer()
    uload = Integer()
    souls_onboard = Integer()
    all_weights_unit = String(
        data_key = 'weights_unit',
        required = True,
        validate = OneOf(VALID_WEIGHT_UNITS))
    print_time_gmt = DateTime(data_key='message_date', format=PRINT_DATETIME_FORMAT)

    actual_takeoff_fuel = Integer(required=False)
    actual_zero_fuel_weight = Integer(required=False)
    center_of_gravity = Float(data_key='cg_percent_mac', required=False)
    dry_operating_weight = Integer(required=False)

    estimated_total_traffic_load = Integer(data_key='gross')

    @post_load
    def post_load(self, data, **kwargs):
        """
        Validate fields.
        """
        if not (data.get('company') or data.get('airline_designator')):
            raise ValidationError('company or airline_designator must exist')
        return data
