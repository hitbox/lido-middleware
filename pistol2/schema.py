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
from marshmallow.fields import Time
from marshmallow.validate import Length
from marshmallow.validate import OneOf
from marshmallow.validate import Range
from marshmallow.validate import Regexp

from extradata import airline_designators
from extradata import stations
from message_to_airlinemap import airline_from_toaddr
from schema import CommonSchemaMixin
from schema import PRINT_DATETIME_FORMAT
from units import VALID_WEIGHT_UNITS

from .regex import company_and_flight_number_re
from .regex import valid_config_name_pattern
from .regex import valid_weight_name_pattern

_max_six_digits = 999_999

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


def merge_or_raise(data, key1, key2):
    """
    Merge key1 and key2 on their common prefix, removing them. Raise if their
    values do not match.

    :param data: data to work on.
    :param keys: positional args of keys with a common prefix.
    """
    prefix = ''
    for char1, char2 in zip(key1, key2):
        if char1 != char2:
            break
        prefix += char1
    if prefix == '':
        raise ValidationError('prefix not found for keys, %r', [key1, key2])
    if data[key1] != data[key2]:
        raise ValidationError('values do not match for merge into key %s' % prefix)
    data[prefix] = data[key1]
    del data[key1]
    del data[key2]

class LoadPlanSchema(CommonSchemaMixin, Schema):
    """
    Pistol Load Plan Schema
    """

    @pre_load
    def pre_load(self, data, **kwargs):
        merge_or_raise(data, 'aircraft_registration1', 'aircraft_registration2')
        merge_or_raise(data, 'day1', 'day2')
        merge_or_raise(data, 'company_and_flight_number1', 'company_and_flight_number2')

        # split and fill iata and icao origin/destination
        for prefix in ['origin', 'destination']:
            full = stations.filled(data[prefix + '_iata_or_icao'])
            del data[prefix + '_iata_or_icao']
            data[prefix + '_iata'] = full['iata']
            data[prefix + '_icao'] = full['icao']

        # plucking data out of the weights list
        def _find(iter_, name, key=None):
            i = (item for item in iter_ if item['name'] == name)
            result = next(i, None)
            if key is not None and result is not None:
                result = result[key]
            return result

        # bring takeoff fuel weight out
        data['actual_takeoff_fuel'] = _find(data['weights'], 'Takeoff', 'weight')

        # bring actual zero fuel weight out
        data['actual_zero_fuel_weight'] = _find(data['weights'], 'Zero Fuel', 'weight')

        # bring center of gravity percent mac and dry operating weight out
        oew = _find(data['weights'], 'OEW')
        if oew is None:
            data['cg_percent_mac'] = None
            data['dry_operating_weight'] = None
        else:
            data['cg_percent_mac'] = oew['cg_percent_mac']
            data['dry_operating_weight'] = oew['weight']

        # bring cargo weight
        data['cargo_weight_for_estimated_total_traffic_load'] = _find(
                data['aircraft_configurations'], 'Cargo Wt', 'value')

        # bring revenue weight
        data['revenue_weight'] = _find(data['aircraft_configurations'], 'Revenue Wt', 'value')

        # split company and flight number
        match = company_and_flight_number_re.match(data['company_and_flight_number'])
        if not match:
            raise ValidationError(
                'Unable to split company and flight number in %r',
                data['company_and_flight_number'])
        data.update(match.groupdict())
        del data['company_and_flight_number']

        data['company'] = data['company'][:3]

        if data['company'] == 'AMZ':
            data['company'] = airline_from_toaddr(data['message_to'])

        # Update airline designator from company value.
        data['airline_designator'] = airline_designators.by_company[data['company']]

        data['flight_number'] = data['flight_number'].replace('CMBDQ', '00')

        if data['flight_number'][-1] in string.ascii_uppercase:
            # optional operational_suffix is present at end of flight_number,
            # strip it off and put it where it belongs
            data['operational_suffix'] = data['flight_number'][-1]
            data['flight_number'] = data['flight_number'][:-1]

        return data

    ad_unknown1 = String()
    ad_unknown2 = String()

    planning_status = Constant('55')
    estimated_total_traffic_load = Integer()
    payload = Integer()

    load_planner = String()
    company = String()
    airline_designator = String(validate=Length(max=3))
    flight_number = String(validate=Length(max=5))
    operational_suffix = String(missing='', validate=OneOf(string.ascii_uppercase))
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

    weights = List(Nested(WeightSchema))
    aircraft_configurations = List(Nested(AircraftConfigSchema))

    actual_takeoff_fuel = Integer(missing=0, validate=Range(max=_max_six_digits))
    actual_zero_fuel_weight = Integer(missing=0, validate=Range(max=_max_six_digits))
    center_of_gravity = Float(data_key='cg_percent_mac', missing=None)
    dry_operating_weight = Integer(validate=Range(max=_max_six_digits))
    cargo_weight = Integer(data_key='revenue_weight')
    cargo_weight_for_estimated_total_traffic_load = Integer()

    # to addresses from email:
    message_to = List(String())

    @post_load
    def post_load(self, data, **kwargs):
        # estimated total traffic load extraction or calculation
        is_combi = any(row for row in data['aircraft_configurations']
                       if row['name'].lower().startswith('fwd acm'))
        if is_combi:
            estimated_total_traffic_load = data['payload']
        else:
            if data['souls_onboard'] > 1:
                # what is ACM?
                acm = data['souls_onboard'] - 2
            else:
                acm = 0
            cargo_weight = data['cargo_weight_for_estimated_total_traffic_load']
            estimated_total_traffic_load = cargo_weight + (acm * 220)
        data['estimated_total_traffic_load'] = estimated_total_traffic_load

        return data


def main(argv=None):
    """
    Extract and schema.load pistol message from file.
    """
    import argparse
    import pickle
    import pprint

    from . import extract

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('emailfile', help='Pickle email file')
    args = parser.parse_args(argv)

    with open(args.emailfile, 'rb') as src_fp:
        email = pickle.load(src_fp)
        loadplan_data = extract.loadplan_from_message(email)
        data = LoadPlanSchema().load(loadplan_data)
        pprint(data)

if __name__ == '__main__':
    main()
