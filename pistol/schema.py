from marshmallow import Schema
from marshmallow import fields
from marshmallow import post_load
from marshmallow.validate import OneOf
from marshmallow.validate import Regexp

from loadplan import AircraftConfig
from loadplan import LoadPlan
from loadplan import Position
from loadplan import Weight
from pistol.regex import valid_config_name_pattern
from pistol.regex import valid_weight_name_pattern
from units import VALID_WEIGHT_UNITS

PRINT_DATETIME_FORMAT = '%m/%d/%y %H%M'

class PositionSchema(Schema):

    position = fields.String()
    unit_load_device = fields.String(allow_none=True)
    destination = fields.String(allow_none=True)
    weight = fields.Integer(allow_none=True)
    weight_unit = fields.String(allow_none=True, validate=OneOf(VALID_WEIGHT_UNITS))
    building = fields.String(allow_none=True)

    @post_load
    def make_object(self, data, **kwargs):
        return Position(**data)


class WeightSchema(Schema):

    name = fields.String(validate=Regexp(valid_weight_name_pattern))
    weight = fields.Integer(allow_none=True)
    forward = fields.Float(allow_none=True)
    cg_percent_mac = fields.Float(allow_none=True)
    aft = fields.Float(allow_none=True)

    @post_load
    def make_object(self, data, **kwargs):
        return Weight(**data)


class AircraftConfigSchema(Schema):

    name = fields.String(validate=Regexp(valid_config_name_pattern))
    value = fields.String()

    @post_load
    def make_object(self, data, **kwargs):
        return AircraftConfig(**data)


class LoadPlanSchema(Schema):

    load_planner = fields.String()
    company = fields.String()
    flight_number = fields.String()
    aircraft_registration = fields.String()
    actual_departure_time = fields.Time(allow_none=True, format='%H%M')
    origin_station = fields.String()
    destination_station = fields.String()
    souls_onboard = fields.Integer()
    color_code = fields.String()
    all_weights_unit = fields.String(validate=OneOf(VALID_WEIGHT_UNITS))
    pistol_version = fields.String()
    computer = fields.String()
    print_time_local = fields.DateTime(format=PRINT_DATETIME_FORMAT)
    print_time_gmt = fields.DateTime(format=PRINT_DATETIME_FORMAT)

    positions = fields.List(fields.Nested(PositionSchema))
    weights = fields.List(fields.Nested(WeightSchema))
    aircraft_configurations = fields.List(fields.Nested(AircraftConfigSchema))

    @post_load
    def make_object(self, data, **kwargs):
        return LoadPlan(**data)
