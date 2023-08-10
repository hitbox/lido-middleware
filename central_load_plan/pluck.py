import argparse
import xml.etree.ElementTree as ET

from pprint import pprint
from types import NoneType

from .exception import CentralLoadPlanError

# expected keys and callable for default type value
DEFAULT_DATA = dict(
    flight_plan_id = NoneType,
    leg_departure_date_utc = NoneType,
    flight_origin_date = NoneType,
    version_number = NoneType,
    flight_number = NoneType,
    airline_iata_code = NoneType,
    flight_identifier = NoneType,
    flight_identifier_first_three = NoneType,
    origin_iata = NoneType,
    destination_iata = NoneType,
    aircraft_registration = NoneType,
    estimated_block_time = NoneType,
    scheduled_departure_time = NoneType,
    estimated_departure_time = NoneType,
    estimated_time_enroute = NoneType,
    planned_payload = NoneType,
    planned_payload_unit = NoneType,
    ramp_fuel = NoneType,
    ramp_fuel_unit = NoneType,
    fuel_burn = NoneType,
    fuel_burn_unit = NoneType,
    taxi_fuel = NoneType,
    taxi_fuel_unit = NoneType,
    landing_fuel = NoneType,
    landing_fuel_unit = NoneType,
    takeoff_fuel = NoneType,
    takeoff_fuel_unit = NoneType,
    ballast_fuel = NoneType,
    ballast_fuel_unit = NoneType,
    mzfw = NoneType,
    mzfw_unit = NoneType,
    mtow = NoneType,
    mtow_unit = NoneType,
    mldg = NoneType,
    mldg_unit = NoneType,
    dow = NoneType,
    dow_unit = NoneType,
    aircraft_equipment_status = list,
    crewmembers = list,
)

def default_data():
    data = {key: type_() for key, type_ in DEFAULT_DATA.items()}
    return data

def _ignore_ns(tag):
    return f'{{*}}{tag}'

def _xmlpath(*tags):
    """
    Prepend tag with namespace ignoring pattern, join with forward slashes and
    prepend entire string with xpath expression to search relative.
    """
    tags_string = '/'.join(map(_ignore_ns, tags))
    return f'./{tags_string}'

def fromxml_update(root, data):
    """
    Pluck values from Operational Flight Plan XML file and update given dict.
    """
    # NOTE: root is <FlightPlan>
    # flight plan id
    data['flight_plan_id'] = root.attrib['flightPlanId']

    # leg departure date in UTC
    elem = root.find(_xmlpath(
        'M633SupplementaryHeader',
        'Flight',
    ))
    data['leg_departure_date_utc'] = elem.attrib['scheduledTimeOfDeparture']
    data['flight_origin_date'] = elem.attrib['flightOriginDate']

    # version number
    # NOTE: VER NO
    # endswith to ignore namespace
    if not root.tag.endswith('FlightPlan'):
        raise CentralLoadPlanError('root tag is not FlightPlan')
    data['version_number'] = root.attrib['flightPlanId']

    # flight
    elem = root.find(_xmlpath(
        'M633SupplementaryHeader',
        'Flight',
        'FlightIdentification',
        'FlightNumber',
    ))
    data['flight_number'] = elem.attrib['number']
    data['airline_iata_code'] = elem.attrib['airlineIATACode']

    elem = root.find(_xmlpath(
        'M633SupplementaryHeader',
        'Flight',
        'FlightIdentification',
        'FlightIdentifier',
    ))
    data['flight_identifier'] = elem.text
    data['flight_identifier_first_three'] = data['flight_identifier'][:3]

    # origin station IATA
    elem = root.find(_xmlpath(
        'M633SupplementaryHeader',
        'Flight',
        'DepartureAirport',
        'AirportIATACode',
    ))
    data['origin_iata'] = elem.text

    # destination station IATA
    elem = root.find(_xmlpath(
        'M633SupplementaryHeader',
        'Flight',
        'ArrivalAirport',
        'AirportIATACode',
    ))
    data['destination_iata'] = elem.text

    # aircraft registration
    elem = root.find(_xmlpath(
        'M633SupplementaryHeader',
        'Aircraft',
    ))
    data['aircraft_registration'] = elem.attrib['aircraftRegistration']

    # estimated block time
    elem = root.find(_xmlpath(
        'FlightPlanSummary',
        'BlockTime',
        'EstimatedTime',
        'Value',
    ))
    data['estimated_block_time'] = elem.text

    # scheduled time of departure
    elem = root.find(_xmlpath(
        'M633SupplementaryHeader',
        'Flight',
    ))
    data['scheduled_departure_time'] = elem.attrib['scheduledTimeOfDeparture']

    # estimated departure time
    # XXX
    # etd same as std
    elem = root.find(_xmlpath(
        'M633SupplementaryHeader',
        'Flight',
    ))
    data['estimated_departure_time'] = elem.attrib['scheduledTimeOfDeparture']

    # estimated time enroute
    elem = root.find(_xmlpath(
        'FlightPlanSummary',
        'FlightTime',
        'EstimatedTime',
        'Value',
    ))
    data['estimated_time_enroute'] = elem.text

    # planned payload
    elem = root.find(_xmlpath(
        'WeightHeader',
        'Load',
        'EstimatedWeight',
        'Value',
    ))
    data['planned_payload'] = elem.text
    # XXX
    # observed kg and lb but template says "all unites in LB"
    data['planned_payload_unit'] = elem.attrib['unit']

    # ramp fuel
    elem = root.find(_xmlpath(
        'FuelHeader',
        'BlockFuel',
        'EstimatedWeight',
        'Value',
    ))
    data['ramp_fuel'] = elem.text
    data['ramp_fuel_unit'] = elem.attrib['unit']

    # fuel burn
    elem = root.find(_xmlpath(
        'FuelHeader',
        'TripFuel',
        'EstimatedWeight',
        'Value',
    ))
    data['fuel_burn'] = elem.text
    data['fuel_burn_unit'] = elem.attrib['unit']

    # taxi fuel
    elem = root.find(_xmlpath(
        'FuelHeader',
        'TaxiFuel',
        'EstimatedWeight',
        'Value',
    ))
    data['taxi_fuel'] = elem.text
    data['taxi_fuel_unit'] = elem.attrib['unit']

    # landing fuel
    elem = root.find(_xmlpath(
        'FuelHeader',
        'LandingFuel',
        'EstimatedWeight',
        'Value',
    ))
    data['landing_fuel'] = elem.text
    data['landing_fuel_unit'] = elem.attrib['unit']

    # take off fuel
    elem = root.find(_xmlpath(
        'FuelHeader',
        'TakeOffFuel',
        'EstimatedWeight',
        'Value',
    ))
    data['takeoff_fuel'] = elem.text
    data['takeoff_fuel_unit'] = elem.attrib['unit']

    # XXX
    # can there be more than one of these?
    # observed zero
    ballast_fuel_elem = root.find(
        './/*{*}AdditionalFuel[@reason="BallastFuel"]')
    ballast_fuel_elem = root.find(_xmlpath(
        './/*{*}AdditionalFuel[@reason="BallastFuel"]'))
    if ballast_fuel_elem:
        ballast_fuel_elem = ballast_fuel_elem.find(
            './{*}EstimatedWeight/{*}Value')
        data['ballast_fuel'] = ballast_fuel_elem.text
        data['ballast_fuel_unit'] = ballast_fuel_elem.attrib['unit']

    # mzfw
    elem = root.find(_xmlpath(
        'WeightHeader',
        'ZeroFuelWeight',
        'StructuralLimit',
        'Value',
    ))
    data['mzfw'] = elem.text
    data['mzfw_unit'] = elem.attrib['unit']

    # Maximum Take Off Weight
    elem = root.find(_xmlpath(
        'WeightHeader',
        'TakeoffWeight',
        'OperationalLimit',
        'Value'
    ))
    data['mtow'] = elem.text
    data['mtow_unit'] = elem.attrib['unit']

    # Maximum Landing Weight
    elem = root.find(_xmlpath(
        'WeightHeader',
        'LandingWeight',
        'OperationalLimit',
        'Value',
    ))
    data['mldg'] = elem.text
    data['mldg_unit'] = elem.attrib['unit']

    # dry operating weight
    elem = root.find(_xmlpath(
        'WeightHeader',
        'DryOperatingWeight',
        'EstimatedWeight',
        'Value',
    ))
    data['dow'] = elem.text
    data['dow_unit'] = elem.attrib['unit']

    # MEL CDL Items
    for melcdlitemelem in root.findall('.//*{*}MELCDLItems/{*}MELCDLItem'):
        melcdlitem = dict(
            item = melcdlitemelem.find('{*}ReferenceId').text
        )
        # XXX
        # observed these without <Title>
        # some have <Remark> instead
        # alert team
        title = melcdlitemelem.find('{*}Title')
        if title is None:
            melcdlitem['description'] = None
        else:
            melcdlitem['description'] = title.text
        data['aircraft_equipment_status'].append(melcdlitem)

def main(argv=None):
    """
    Dump data extracted from XML.
    """
    parser = argparse.ArgumentParser(
        description = main.__doc__,
    )
    parser.add_argument('srcxml')
    args = parser.parse_args(argv)

    tree = ET.parse(args.srcxml)
    root = tree.getroot()
    data = default_data()
    fromxml_update(root, data)
    pprint(data)

if __name__ == '__main__':
    main()
