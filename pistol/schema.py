from operator import xor

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
from marshmallow.fields import Time
from marshmallow.validate import OneOf
from marshmallow.validate import Regexp

from extradata import airline_designators
from extradata import stations
from units import VALID_WEIGHT_UNITS

from .regex import valid_config_name_pattern
from .regex import valid_weight_name_pattern

PRINT_DATETIME_FORMAT = '%m/%d/%y %H%M'

class PositionSchema(Schema):
    """
    Pistol Position Schema
    """

    position = String()
    unit_load_device = String(allow_none=True)
    destination_icao = String(allow_none=True)
    destination_iata = String(allow_none=True)
    weight = Integer(allow_none=True)
    weight_unit = String(allow_none=True, validate=OneOf(VALID_WEIGHT_UNITS))
    building = String(allow_none=True)

    @pre_load
    def update_other_station(self, data, **kwargs):
        """
        Validate that one or the other (IATA/ICAO) station is present, but not
        both, and update the other.
        """
        stations.update_other_station_by_type(data, 'destination')
        return data

    @post_load
    def validate_station_types(self, data, **kwargs):
        """
        Validate that if one type of station is set, both are.
        """
        iata = bool(data['destination_iata'])
        icao = bool(data['destination_icao'])
        either = iata or icao
        both = iata and icao
        if either and not both:
            raise ValidationError('If one station type is set, both must be')
        return data


class WeightSchema(Schema):
    """
    Pistol Weight Schema
    """

    name = String(validate=Regexp(valid_weight_name_pattern))
    weight = Integer(allow_none=True)
    forward = Float(allow_none=True)
    cg_percent_mac = Float(allow_none=True)
    aft = Float(allow_none=True)


class AircraftConfigSchema(Schema):
    """
    Pistol Aircraft Configuration Schema
    """

    name = String(validate=Regexp(valid_config_name_pattern))
    value = String()


class LoadPlanSchema(Schema):
    """
    Pistol Load Plan Schema
    """

    load_planner = String()
    company = String()
    airline_designator = String()
    flight_number = String()
    aircraft_registration = String()
    actual_departure_time = Time(allow_none=True, format='%H%M')
    origin_icao = String(required=True)
    origin_iata = String(required=True)
    destination_icao = String(required=True)
    destination_iata = String(required=True)
    day = Integer()
    souls_onboard = Integer()
    color_code = String()
    all_weights_unit = String(validate=OneOf(VALID_WEIGHT_UNITS))
    pistol_version = String()
    computer = String()
    print_time_local = DateTime(format=PRINT_DATETIME_FORMAT)
    print_time_gmt = DateTime(format=PRINT_DATETIME_FORMAT)

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
    weights = List(Nested(WeightSchema))
    aircraft_configurations = List(Nested(AircraftConfigSchema))

    # filled by pre-loads below, same name, prefixed with underscore
    actual_takeoff_fuel = Integer()
    actual_zero_fuel_weight = Integer()
    center_of_gravity = Float(data_key='cg_percent_mac')
    dry_operating_weight = Integer()

    @pre_load
    def _actual_takeoff_fuel(self, data, **kwargs):
        for weight in data['weights']:
            if weight['name'] == 'Takeoff':
                value = weight['weight']
                break
        else:
            value = None
        data['actual_takeoff_fuel'] = value
        return data

    @pre_load
    def _actual_zero_fuel_weight(self, data, **kwargs):
        for weight in data['weights']:
            if weight['name'] == 'Zero Fuel':
                data['actual_zero_fuel_weight'] = weight['weight']
        return data

    @pre_load
    def _center_of_gravity(self, data, **kwargs):
        for weight in data['weights']:
            if weight['name'] == 'OEW':
                data['cg_percent_mac'] = weight['cg_percent_mac']
        return data

    @pre_load
    def _dry_operating_weight(self, data, **kwargs):
        """
        Dry operating weight from operating empty weight
        """
        value = None
        for weight in data['weights']:
            if weight['name'] == 'OEW':
                value = weight['weight']
        data['dry_operating_weight'] = value
        return data

    @pre_load
    def update_other_station_type(self, data, **kwargs):
        """
        Validate that one or the other (IATA/ICAO) station is present, but not
        both, and update the other
        """
        for field in ['destination', 'origin']:
            stations.update_other_station_by_type(data, field)
        return data

    @pre_load
    def update_airline_designator_from_company(self, data, **kwargs):
        """
        Update airline designator from company value.
        """
        company = data['company']
        data['airline_designator'] = airline_designators.by_company[company]
        return data
