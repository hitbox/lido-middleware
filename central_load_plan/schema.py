import argparse
import sys
import xml.etree.ElementTree as ET

from datetime import timedelta

from marshmallow import Schema
from marshmallow import post_load
from marshmallow.fields import DateTime
from marshmallow.fields import Date
from marshmallow.fields import Integer
from marshmallow.fields import List
from marshmallow.fields import Nested
from marshmallow.fields import String
from marshmallow.fields import Time
from marshmallow.validate import OneOf
from marshmallow.validate import ValidationError

from . import pluck

# ex: PT1H30M45S
DURATION_FMT = 'PT%HH%MM%SS'

class MELCDLItemSchema(Schema):

    item = String()
    description = String(allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        item = data['item']
        if item.endswith('00-30-FAK'):
            fak_status = 0
        elif item.endswith('FAK'):
            fak_status = 1
        else:
            fak_status = 99
        data['fak_status'] = fak_status
        return data


class CrewSchema(Schema):

    seat = String()
    first_name = String()
    last_name = String()
    employee_number = String()


class OperationalFlightPlanSchema(Schema):
    """
    Marshal the Operational Flight Plan XML data.
    """

    date_format = '%Y-%m-%dZ'
    datetime_format = '%Y-%m-%dT%H:%M:%SZ'
    units = ['kg', 'lb']

    flight_plan_id = String()
    leg_departure_date_utc = DateTime(format=datetime_format)
    flight_origin_date = Date(format=date_format)
    version_number = String()
    flight_number = Integer()
    flight_identifier = String()
    flight_identifier_first_three = String()
    airline_iata_code = String()
    origin_iata = String()
    destination_iata = String()
    aircraft_registration = String()

    estimated_block_time = Time(format=DURATION_FMT)
    estimated_time_enroute = Time(format=DURATION_FMT)

    scheduled_departure_time = DateTime(format=datetime_format)
    estimated_departure_time = DateTime(format=datetime_format)

    planned_payload = Integer()
    planned_payload_unit = String(validate=OneOf(units))

    ramp_fuel = Integer()
    ramp_fuel_unit = String(validate=OneOf(units))

    fuel_burn = Integer()
    fuel_burn_unit = String(validate=OneOf(units))

    taxi_fuel = Integer()
    taxi_fuel_unit = String(validate=OneOf(units))

    takeoff_fuel = Integer()
    takeoff_fuel_unit = String(validate=OneOf(units))

    landing_fuel = Integer()
    landing_fuel_unit = String(validate=OneOf(units))

    ballast_fuel = Integer(allow_none=True)
    ballast_fuel_unit = String(allow_none=True, validate=OneOf(units))

    mzfw = Integer()
    mzfw_unit = String(validate=OneOf(units))

    mtow = Integer()
    mtow_unit = String(validate=OneOf(units))

    mldg = Integer()
    mldg_unit = String(validate=OneOf(units))

    dow = Integer()
    dow_unit = String(validate=OneOf(units))

    aircraft_equipment_status = List(Nested(MELCDLItemSchema))
    crewmembers = List(Nested(CrewSchema))

    @post_load
    def post_load(self, data, **kwargs):
        # raise for mixed units
        units = set()
        for key, value in data.items():
            if key.endswith('_unit') and value is not None:
                units.add(value)
        if len(units) != 1:
            raise ValidationError('Mixed units %r' % units)

        # calculate estimated arrival time
        etd = data['estimated_departure_time']
        ste = data['estimated_block_time']
        data['estimated_arrival_time'] = etd + timedelta(hours=ste.hour, minutes=ste.minute)

        # calculate max payload
        calcs = [
            data['mtow'] - data['takeoff_fuel'] - data['dow'],
            data['mldg'] - data['landing_fuel'] - data['dow'],
            data['mzfw'] - data['dow'],
        ]
        data['max_payload'] = min(calcs)

        return data


class SMTPConfSchema(Schema):
    host = String()
    port = Integer()


class OracleConfSchema(Schema):
    oracle_lib_dir = String()
    drivername = String()
    host = String()
    port = Integer()
    username = String()
    password = String()
    database = String()


smtpconfschema = SMTPConfSchema()
oracleconfschema = OracleConfSchema()
ofpschema = OperationalFlightPlanSchema()

def main(argv=None):
    """
    Convert XML to data.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('xmlfiles', nargs='+')
    args = parser.parse_args(argv)

    for xmlfile in args.xmlfiles:
        print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        data = pluck.fromxml(root)
        data = OperationalFlightPlanSchema().load(data)

if __name__ == '__main__':
    sys.exit(main())
