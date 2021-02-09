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
    """
    Sable Position Schema
    """

    @pre_load
    def pre_load(self, data, **kwargs):
        data = ((k, v.strip()) for k, v in data.items())
        data = {k: None if not v else v for k,v in data}
        return data

    position = String(data_key='POS')
    destination_iata = String(allow_none=True, data_key='DST')
    unit_load_device = String(data_key='ULDNUMBER')
    tare = Integer(allow_none=True, data_key='TARE')
    net_weight = Integer(allow_none=True, data_key='NETT')
    total = Integer(allow_none=True, data_key='TOTAL')
    flag = String(allow_none=True, data_key='FLAG')
    volume = String(allow_none=True, data_key='VOL')


class LoadPlanSchema(CommonSchemaMixin, Schema):
    """
    Sable Load Plan Schema
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

    flight_number = String(required=True)
    company = String(allow_none=True, required=True)
    airline_designator = String(allow_none=True, required=True, validate=Length(max=3))
    day = Integer(required=True)
    tail = String()
    origin_iata = String(required=True, validate=Length(max=3))
    destination_iata = String(required=True, validate=Length(max=3))
    gross = Integer()
    net_weight = Integer()
    uload = Integer()
    souls_onboard = Integer()
    all_weights_unit = String(
        data_key = 'weights_unit',
        required = True,
        validate = OneOf(VALID_WEIGHT_UNITS))
    print_time_gmt = DateTime(data_key='message_date', format=PRINT_DATETIME_FORMAT)

    #positions = List(Nested(PositionSchema))

    actual_takeoff_fuel = Integer(required=True)
    actual_zero_fuel_weight = Integer(required=True)
    center_of_gravity = Float(data_key='cg_percent_mac', required=True)
    dry_operating_weight = Integer(required=True)

    @post_load
    def post_load(self, data, **kwargs):
        """
        Validate fields.
        """
        if not (data.get('company') or data.get('airline_designator')):
            raise ValidationError('company or airline_designator must exist')
        return data
