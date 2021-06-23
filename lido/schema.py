from marshmallow import Schema
from marshmallow.fields import Constant
from marshmallow.fields import DateTime
from marshmallow.fields import Float
from marshmallow.fields import Integer
from marshmallow.fields import String
from marshmallow.validate import OneOf

from .constants import VALID_AIRLINE_DESIGNATOR
from .constants import VALID_MEASURE_UNIT
from .constants import VALID_OPERATIONAL_SUFFIX
from .constants import VALID_PLANNING_STATUS
from .constants import YESNO
from .constants import YESNO_NONE

class LIDOWeightBalanceSchema(Schema):
    """
    Schema of the data structure expected by the LIDO message renderer.
    """

    message_type = Constant('WAB')
    timestamp_in_gmt = DateTime()
    airline_designator = String(validate=OneOf(VALID_AIRLINE_DESIGNATOR))
    flight_number = String()
    operational_suffix = String(validate=OneOf(VALID_OPERATIONAL_SUFFIX))
    date_of_origin = DateTime()
    departure_airport_iata = String()
    destination_airport_iata = String()
    planning_status = String(validate=OneOf(VALID_PLANNING_STATUS))
    duplicate_number = Integer(default=1)
    revision_number = Integer(default=0)
    dry_operating_weight = Integer()
    estimated_total_traffic_load = Integer(allow_none=True)
    pax_baggage_indicator = String(validate=OneOf(YESNO))
    cargo_mail_indicator = String(validate=OneOf(YESNO))
    transit_load_indicator = String(validate=OneOf(YESNO))
    tail_tank_indicator = String(allow_none=True, validate=OneOf(YESNO_NONE))
    center_of_gravity = Float(allow_none=True)
    actual_zero_fuel_weight = Integer()
    actual_takeoff_fuel = Integer()
    estimated_pax = Integer()
    unit_of_measure = String(validate=OneOf(VALID_MEASURE_UNIT))
    dry_operating_index = Integer(allow_none=True)
    cargo_weight = Integer()
    separator = Constant(' ' * 18)
    estimated_pax_class_one = Integer(allow_none=True)
    estimated_pax_class_two = Integer(allow_none=True)
    estimated_pax_class_three = Integer(allow_none=True)
