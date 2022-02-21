import re

from marshmallow.fields import Constant
from marshmallow.fields import Float
from marshmallow.fields import Integer
from marshmallow.fields import List
from marshmallow.fields import Nested
from marshmallow.fields import String
from marshmallow.validate import Length
from marshmallow.validate import OneOf

PRINT_DATETIME_FORMAT = '%m/%d/%y %H%M'

class CommonSchemaMixin:

    planning_status = Constant('04', validate=Length(max=2))
    duplicate_number = Constant('1', validate=Length(max=1))
    revision_number = Constant('00', validate=Length(max=2))
    operational_suffix = Constant(' ', validate=Length(max=1))
    pax_baggage_indicator = Constant('Y', validate=OneOf('YN'))
    cargo_mail_indicator = Constant('Y', validate=OneOf('YN'))
    transit_load_indicator = Constant('Y', validate=OneOf('YN'))
    tail_tank_indicator = Constant(' ', validate=Length(max=1))
    estimated_pax = Constant(0)
    dry_operating_index = Constant(None)
    estimated_pax_class_one = Constant(None)
    estimated_pax_class_two = Constant(None)
    estimated_pax_class_three = Constant(None)


def only_digits(string):
    """
    Return `string` with only digits and leading zeros removed. Like an integer
    but still a string.
    """
    # strip non-digits
    string = ''.join(char for char in string if char.isdigit())
    # strip leading zeros
    while string and string[0] == '0':
        string = string[1:]
    return string

mid_digits_re = re.compile('^\D*(\d+)(\D|$)')

def mid_digits(string):
    """
    Return inner digits, ignoring trailing digits and alpha chars. Strip
    leading zeros.
    """
    result = ''
    match = mid_digits_re.match(string)
    if match:
        result = match.group(1)
        result = result.lstrip('0')
    return result
