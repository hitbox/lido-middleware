from datetime import timedelta

from marshmallow import Schema
from marshmallow import post_load
from marshmallow.fields import Constant
from marshmallow.fields import DateTime
from marshmallow.fields import Integer
from marshmallow.fields import List
from marshmallow.fields import Nested
from marshmallow.fields import String
from marshmallow.fields import Time
from marshmallow.validate import Length
from marshmallow.validate import OneOf
from marshmallow.validate import ValidationError

class WSIWeatherSchema(Schema):

    message_identifier = Constant('WXL')
    number_of_messages = Constant(1)
    separator = Constant(' ' * 4)
    icao_originator = String(validate=Length(4, 4))
    weather_identifier = Constant('FT', validate=Length(2, 2))
    time_of_observation = DateTime('%Y%m%dT%H%M%SZ')
    remark = String()
    input_office = Constant('C')
    start_of_validity = String(validate=Length(6, 6))
    end_of_validity = String(validate=Length(6, 6))
    weather_text = String(validate=Length(1, 999))


def main(argv=None):
    """
    Convert XML to data.
    """
    import argparse
    import xml.etree.ElementTree as ET

    from pprint import pprint

    from . import pluck

    parser = argparse.ArgumentParser()
    parser.add_argument('xmlfiles', nargs='+')
    args = parser.parse_args(argv)

    for xmlfile in args.xmlfiles:
        print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        data = pluck.fromxml(root)
        data = WSIWeatherSchema().load(data)
        pprint(data)

if __name__ == '__main__':
    main()
