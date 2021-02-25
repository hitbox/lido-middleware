from marshmallow import Schema
from marshmallow import post_load
from marshmallow import pre_load
from marshmallow import validates
from marshmallow.exceptions import ValidationError
from marshmallow.fields import Constant
from marshmallow.fields import DateTime
from marshmallow.fields import Float
from marshmallow.fields import Integer
from marshmallow.fields import List
from marshmallow.fields import Nested
from marshmallow.fields import String
from marshmallow.fields import Time
from marshmallow.validate import Length
from marshmallow.validate import OneOf
from marshmallow.validate import Range
from marshmallow.validate import Regexp

from .regex import company_and_flight_number_re

from extradata import airline_designators
from extradata import stations
from schema import CommonSchemaMixin
from schema import PRINT_DATETIME_FORMAT
from units import VALID_WEIGHT_UNITS

from .regex import valid_config_name_pattern
from .regex import valid_weight_name_pattern

_max_six_digits = 999_999

class PositionSchema(Schema):
    """
    Pistol Position Schema
    """

    @pre_load
    def pre_load(self, position_data, **kwargs):
        """
        Prepare data for loading
        """
        if 'destination_iata_or_icao' in position_data:
            # fill destination iata and icao
            destination_iata_or_icao = position_data['destination_iata_or_icao'].strip()
            del position_data['destination_iata_or_icao']
            if destination_iata_or_icao:
                full = stations.filled(destination_iata_or_icao)
                position_data['destination_iata'] = full['iata']
                position_data['destination_icao'] = full['icao']
        return position_data

    position = String(required=True)
    unit_load_device = String(allow_none=True)
    destination_icao = String(allow_none=True)
    destination_iata = String(allow_none=True)
    weight = Integer(allow_none=True)
    weight_unit = String(allow_none=True, validate=OneOf(VALID_WEIGHT_UNITS))
    building = String(allow_none=True)

    @post_load
    def validate_station_types(self, data, **kwargs):
        """
        Validate that if one type of station is set, both are.
        """
        if 'destination_iata' in data and 'destination_icao' in data:
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

    @pre_load
    def pre_load(self, data, **kwargs):
        for key, value in data.items():
            if value == 'N/A':
                data[key] = None
        return data

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


class LoadPlanSchema(CommonSchemaMixin, Schema):
    """
    Pistol Load Plan Schema
    """

    @pre_load
    def pre_load(self, data, **kwargs):
        # merges with sanity check
        # aircraft_registration
        if data['aircraft_registration1'] != data['aircraft_registration2']:
            raise ValidationError('aircraft registrations do not match')
        data['aircraft_registration'] = data['aircraft_registration1']
        del data['aircraft_registration1']
        del data['aircraft_registration2']

        # day
        if data['day1'] != data['day2']:
            raise ValidationError('day fields do not match')
        data['day'] = data['day1']
        del data['day1']
        del data['day2']

        # split and fill iata and icao origin/destination
        for prefix in ['origin', 'destination']:
            full = stations.filled(data[prefix + '_iata_or_icao'])
            del data[prefix + '_iata_or_icao']
            data[prefix + '_iata'] = full['iata']
            data[prefix + '_icao'] = full['icao']

        # bring takeoff fuel weight out
        for weight in data['weights']:
            if weight['name'] == 'Takeoff':
                data['actual_takeoff_fuel'] = weight['weight']
                break
        else:
            data['actual_takeoff_fuel'] = None

        # bring actual zero fuel weight out
        for weight in data['weights']:
            if weight['name'] == 'Zero Fuel':
                data['actual_zero_fuel_weight'] = weight['weight']
                break
        else:
            data['actual_zero_fuel_weight'] = None

        # bring center of gravity percent mac out
        for weight in data['weights']:
            if weight['name'] == 'OEW':
                data['cg_percent_mac'] = weight['cg_percent_mac']
                break
        else:
            data['cg_percent_mac'] = None

        # dry operating weight from operating empty weight
        value = None
        for weight in data['weights']:
            if weight['name'] == 'OEW':
                data['dry_operating_weight'] = weight['weight']
                break
        else:
            data['dry_operating_weight'] = None

        # split company_flight_number -> company, flight number
        if data['company_and_flight_number1'] != data['company_and_flight_number2']:
            raise ValidationError('company_and_flight_number{1,2} fields do not match')
        company_and_flight_number = data['company_and_flight_number1']
        del data['company_and_flight_number1']
        del data['company_and_flight_number2']

        company, flight_number = split_company_and_flight_number(company_and_flight_number)
        data['company'] = company
        data['flight_number'] = flight_number

        # Update airline designator from company value.
        data['airline_designator'] = airline_designators.by_company[data['company']]

        return data

    ad_unknown1 = String()
    ad_unknown2 = String()

    load_planner = String()
    company = String()
    airline_designator = String(validate=Length(max=3))
    flight_number = String(validate=Length(max=5))
    aircraft_registration = String()
    actual_departure_time = Time(allow_none=True, format='%H%M')
    origin_icao = String(required=True, validate=Length(max=4))
    origin_iata = String(required=True, validate=Length(max=3))
    destination_icao = String(required=True, validate=Length(max=4))
    destination_iata = String(required=True, validate=Length(max=3))
    day = Integer()
    souls_onboard = Integer()
    color_code = String()
    all_weights_unit = String(validate=OneOf(VALID_WEIGHT_UNITS))
    pistol_version = String()
    computer = String()
    print_time_local = DateTime(format=PRINT_DATETIME_FORMAT)
    print_time_gmt = DateTime(format=PRINT_DATETIME_FORMAT)

    #positions = List(Nested(PositionSchema))
    weights = List(Nested(WeightSchema))
    aircraft_configurations = List(Nested(AircraftConfigSchema))

    actual_takeoff_fuel = Integer(validate=Range(max=_max_six_digits))
    actual_zero_fuel_weight = Integer(validate=Range(max=_max_six_digits))
    center_of_gravity = Float(data_key='cg_percent_mac')
    dry_operating_weight = Integer(validate=Range(max=_max_six_digits))


def split_company_and_flight_number(company_and_flight_number):
    mapping = (
        ('ATIATN', 'ATI'),
        ('ABXABX', 'ABX'),
        ('ATI8C', 'ATI'),
        ('ABX', 'ABX'),
        ('ATI', 'ATI'),
    )
    for prefix, company in mapping:
        if company_and_flight_number.startswith(prefix):
            flight_number = company_and_flight_number[len(prefix):][-4:]
            break
    else:
        raise ValidationError(
            'unable to split company and flight number, %r'
            % company_and_flight_number)
    return company, flight_number
