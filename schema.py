from marshmallow.fields import Constant
from marshmallow.fields import Float
from marshmallow.fields import Integer
from marshmallow.fields import List
from marshmallow.fields import Nested
from marshmallow.fields import String
from marshmallow.validate import Length
from marshmallow.validate import OneOf

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
