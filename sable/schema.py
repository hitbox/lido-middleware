from marshmallow import Schema
from marshmallow import post_load
from marshmallow.exceptions import ValidationError
from marshmallow.fields import Constant
from marshmallow.fields import Float
from marshmallow.fields import Integer
from marshmallow.fields import List
from marshmallow.fields import Nested
from marshmallow.fields import String
from marshmallow.validate import OneOf

from units import VALID_WEIGHT_UNITS

class PositionSchema(Schema):
    """
    Sable Position Schema
    """

    position = String(data_key='POS')
    destination_iata = String(allow_none=True, data_key='DST')
    unit_load_device = String(data_key='ULDNUMBER')
    tare = Integer(allow_none=True, data_key='TARE')
    net_weight = Integer(allow_none=True, data_key='NETT')
    total = Integer(allow_none=True, data_key='TOTAL')
    flag = String(allow_none=True, data_key='FLAG')
    volume = String(allow_none=True, data_key='VOL')


class LoadPlanSchema(Schema):
    """
    Sable Load Plan Schema
    """

    flight_number = String(required=True)
    company = String(allow_none=True, required=True)
    airline_designator = String(allow_none=True, required=True)
    day = Integer(required=True)
    tail = String()
    origin_iata = String(required=True)
    destination_iata = String(required=True)
    gross = Integer()
    net_weight = Integer()
    uload = Integer()
    souls_onboard = Integer()
    all_weights_unit = String(
        data_key='weights_unit',
        required=True,
        validate=OneOf(VALID_WEIGHT_UNITS))

    planning_status = Constant('04')
    duplicate_number = Constant('1')
    revision_number = Constant('00')
    operational_suffix = Constant(' ')
    pax_baggage_indicator = Constant('N')
    cargo_mail_indicator = Constant('N')
    transit_load_indicator = Constant('N')
    tail_tank_indicator = Constant(' ')
    estimated_pax = Constant(0)
    dry_operating_index = Constant(None)
    estimated_pax_class_one = Constant(None)
    estimated_pax_class_two = Constant(None)
    estimated_pax_class_three = Constant(None)

    positions = List(Nested(PositionSchema))

    actual_takeoff_fuel = Integer(required=True)
    actual_zero_fuel_weight = Integer(required=True)
    center_of_gravity = Float(data_key='cg_percent_mac', required=True)
    dry_operating_weight = Integer(required=True)

    @post_load
    def validate_company_or_airline_designator(self, data, **kwargs):
        """
        """
        if not (data.get('company') or data.get('airline_designator')):
            raise ValidationError('company or airline_designator must exist')
        return data
