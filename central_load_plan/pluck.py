import argparse
import xml.etree.ElementTree as ET

from pprint import pprint

from .exception import CentralLoadPlanError

def fromxml(root):
    """
    Pluck values from Operational Flight Plan XML file.
    """
    data = {}
    # leg departure date in UTC
    elem = root.find('./{*}M633SupplementaryHeader/{*}Flight')
    data['leg_departure_date_utc'] = elem.attrib['scheduledTimeOfDeparture']
    data['flight_origin_date'] = elem.attrib['flightOriginDate']

    # version number
    elem = root.find('{*}M633Header')
    data['version_number'] = elem.attrib['versionNumber']

    # flight
    elem = root.find(
        './{*}M633SupplementaryHeader'
        '/{*}Flight'
        '/{*}FlightIdentification'
        '/{*}FlightNumber')
    data['flight_number'] = elem.attrib['number']
    data['airline_iata_code'] = elem.attrib['airlineIATACode']

    # origin station IATA
    elem = root.find(
        './{*}M633SupplementaryHeader'
        '/{*}Flight'
        '/{*}DepartureAirport'
        '/{*}AirportIATACode')
    data['origin_iata'] = elem.text

    # destination station IATA
    elem = root.find(
        './{*}M633SupplementaryHeader'
        '/{*}Flight'
        '/{*}ArrivalAirport'
        '/{*}AirportIATACode')
    data['destination_iata'] = elem.text

    # aircraft registration
    elem = root.find('./{*}M633SupplementaryHeader/{*}Aircraft')
    data['aircraft_registration'] = elem.attrib['aircraftRegistration']

    # estimated block time
    elem = root.find(
        './{*}FlightPlanSummary/{*}BlockTime/{*}EstimatedTime/{*}Value')
    data['estimated_block_time'] = elem.text

    # scheduled time of departure
    elem = root.find('./{*}M633SupplementaryHeader/{*}Flight')
    data['scheduled_departure_time'] = elem.attrib['scheduledTimeOfDeparture']

    # estimated departure time
    # XXX
    # etd same as std
    elem = root.find('./{*}M633SupplementaryHeader/{*}Flight')
    data['estimated_departure_time'] = elem.attrib['scheduledTimeOfDeparture']

    # planned payload
    elem = root.find('./{*}WeightHeader/{*}Load/{*}EstimatedWeight/{*}Value')
    data['planned_payload'] = elem.text
    # XXX
    # observed kg and lb but template says "all unites in LB"
    data['planned_payload_unit'] = elem.attrib['unit']

    # ramp fuel
    elem = root.find(
        './{*}FuelHeader/{*}BlockFuel/{*}EstimatedWeight/{*}Value')
    data['ramp_fuel'] = elem.text
    data['ramp_fuel_unit'] = elem.attrib['unit']

    # fuel burn
    elem = root.find('./{*}FuelHeader/{*}TripFuel/{*}EstimatedWeight/{*}Value')
    data['fuel_burn'] = elem.text
    data['fuel_burn_unit'] = elem.attrib['unit']

    # taxi fuel
    elem = root.find('./{*}FuelHeader/{*}TaxiFuel/{*}EstimatedWeight/{*}Value')
    data['taxi_fuel'] = elem.text
    data['taxi_fuel_unit'] = elem.attrib['unit']

    # landing fuel
    elem = root.find(
        './{*}FuelHeader/{*}LandingFuel/{*}EstimatedWeight/{*}Value')
    data['landing_fuel'] = elem.text
    data['landing_fuel_unit'] = elem.attrib['unit']

    # take off fuel
    elem = root.find(
        './{*}FuelHeader/{*}TakeOffFuel/{*}EstimatedWeight/{*}Value')
    data['takeoff_fuel'] = elem.text
    data['takeoff_fuel_unit'] = elem.attrib['unit']

    # XXX
    # can there be more than one of these?
    # observed zero
    ballast_fuel_elem = root.find(
        './/*{*}AdditionalFuel[@reason="BallastFuel"]')
    if ballast_fuel_elem:
        ballast_fuel_elem = ballast_fuel_elem.find(
            './{*}EstimatedWeight/{*}Value')
        data['ballast_fuel'] = ballast_fuel_elem.text
        data['ballast_fuel_unit'] = ballast_fuel_elem.attrib['unit']
    else:
        data['ballast_fuel'] = None
        data['ballast_fuel_unit'] = None

    # mzfw
    elem = root.find('./{*}WeightHeader/{*}ZeroFuelWeight/{*}StructuralLimit/{*}Value')
    data['mzfw'] = elem.text
    data['mzfw_unit'] = elem.attrib['unit']

    # Maximum Take Off Weight
    elem = root.find('./{*}WeightHeader/{*}TakeoffWeight/{*}OperationalLimit/{*}Value')
    data['mtow'] = elem.text
    data['mtow_unit'] = elem.attrib['unit']

    # Maximum Landing Weight
    elem = root.find('./{*}WeightHeader/{*}LandingWeight/{*}OperationalLimit/{*}Value')
    data['mldg'] = elem.text
    data['mldg_unit'] = elem.attrib['unit']

    # dry operating weight
    elem = root.find('./{*}WeightHeader/{*}DryOperatingWeight/{*}EstimatedWeight/{*}Value')
    data['dow'] = elem.text
    data['dow_unit'] = elem.attrib['unit']

    # MEL CDL Items
    data['aircraft_equipment_status'] = []
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
    #
    data['crewmembers'] = []
    return data

def main(argv=None):
    """
    Process XML files into CLP email messages and send.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('xmlfile')
    args = parser.parse_args(argv)
    tree = ET.parse(args.xmlfile)
    root = tree.getroot()
    data = fromxml(root)
    pprint(data)

if __name__ == '__main__':
    main()
