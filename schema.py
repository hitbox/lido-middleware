import base64
import codecs
import re
import string

import marshmallow

from marshmallow import Schema
from marshmallow.exceptions import ValidationError
from marshmallow.fields import Boolean
from marshmallow.fields import Constant
from marshmallow.fields import DateTime
from marshmallow.fields import Field
from marshmallow.fields import Float
from marshmallow.fields import Integer
from marshmallow.fields import List
from marshmallow.fields import Nested
from marshmallow.fields import String
from marshmallow.validate import Length
from marshmallow.validate import OneOf

from extradata import airline_designators
from extradata import airline_map

PRINT_DATETIME_FORMAT = '%m/%d/%y %H%M'
YN = 'YN'

# split the company and flight number apart with regex
# NOTE: keep longest company strings at front of capture
company_and_flight_number_re = re.compile(
    '^(?P<company>ATIATN|ABXABX|ATI8C|ABX|ATI|ATN|AMZ)(?P<flight_number>\S+)')

class CommonSchemaMixin:
    """
    Schema common to pistol and sable.
    """

    planning_status = Constant('04', validate=Length(max=2))
    duplicate_number = Constant('1', validate=Length(max=1))
    revision_number = Constant('00', validate=Length(max=2))
    operational_suffix = Constant(' ', validate=Length(max=1))
    pax_baggage_indicator = Constant('Y', validate=OneOf(YN))
    cargo_mail_indicator = Constant('Y', validate=OneOf(YN))
    transit_load_indicator = Constant('Y', validate=OneOf(YN))
    tail_tank_indicator = Constant(' ', validate=Length(max=1))
    estimated_pax = Constant(0)
    dry_operating_index = Constant(None)
    estimated_pax_class_one = Constant(None)
    estimated_pax_class_two = Constant(None)
    estimated_pax_class_three = Constant(None)


class Base64ContentField(Field):
    """
    A string (not bytes) of base64 encoded "bytes".
    https://learn.microsoft.com/en-us/graph/api/resources/fileattachment?view=graph-rest-1.0#properties
    See contentBytes
    """

    def _deserialize(self, string_of_bytes, attr, data, **kwargs):
        try:
            return base64.b64decode(string_of_bytes)
        except TypeError:
            raise ValidationError(
                'Base 64 content field must be string or bytes.')


class BodySchema(Schema):

    content = String()
    content_type = String(data_key='contentType')


class EmailAddressSchema(Schema):

    address = String()
    name = String()


class SenderSchema(Schema):

    email_address = Nested(EmailAddressSchema, data_key='emailAddress')


class RecipientSchema(Schema):

    email_address = Nested(EmailAddressSchema, data_key='emailAddress')


class AttachmentSchema(Schema):

    class Meta:
        # ignore metadata like links to the next page and other properties
        # not needed.
        unknown = marshmallow.EXCLUDE


    content_type = String(data_key='contentType')
    content = Base64ContentField(data_key='contentBytes')
    id = String()
    is_inline = Boolean(data_key='isInline')
    last_modified_datetime = DateTime(data_key='lastModifiedDateTime')
    name = String()
    size = Integer()

    @marshmallow.post_load
    def make_expected(self, data, **kwargs):
        class Payload:

            def __init__(self, content):
                self.payload = content


        expected = Payload(data['content'])
        return expected


class MessageSchema(Schema):

    class Meta:
        # ignore metadata like links to next page and other uneeded properties.
        unknown = marshmallow.EXCLUDE


    sender = Nested(SenderSchema)
    toRecipients = Nested(RecipientSchema, many=True)
    subject = String()
    received_datetime = DateTime(data_key='receivedDateTime')
    body = Nested(BodySchema)

    attachments = List(
        Nested(AttachmentSchema)
    )

    @marshmallow.post_load
    def make_like_imap_email(self, data, **kwargs):
        class EmailLike:

            def __init__(self, from_, to, subject, date, body, attachments):
                self.from_ = from_
                self.to = to
                self.subject = subject
                self.date = date
                self.body = body
                self.attachments = attachments


        email_like = EmailLike(
            from_ = data['sender']['email_address']['address'],
            to = [ to_data['email_address']['address'] for to_data in data['toRecipients'] ],
            subject = data['subject'],
            date = data['received_datetime'],
            body = data['body']['content'],
            attachments = data['attachments'],
        )
        return email_like


mid_digits_re = re.compile('^\D*(\d+)(\D|$)')

def mid_digits(flight_number_string):
    """
    Return inner digits, ignoring trailing digits and alpha chars. Strip
    leading zeros.
    """
    result = ''
    match = mid_digits_re.match(flight_number_string)
    if match:
        result = match.group(1)
        result = result.lstrip('0')
    return result

def resolve_company_from_email(company, to_addresses):
    # look up company from to-addresses
    if company == 'AMZ':
        company = airline_map.from_toaddresses(to_addresses)
    return company

def dict_for_company(company, to_addresses):
    """
    Return dict info from company string.
    """
    result = {}
    # keep first three characters of company
    result['company'] = resolve_company_from_email(company[:3], to_addresses)

    # Update airline designator from company value.
    result['airline_designator'] = airline_designators.by_company[result['company']]
    return result

def military_flight_number(flight_number):
    """
    Replace CMBDQ with 00 and CMB with 0.
    """
    return flight_number.replace('CMBDQ', '00').replace('CMB', '0')

def dict_for_flight_number(flight_number):
    """
    Process flight_number string return a dict of parsed out data.
    """
    result = {}

    # parse flight number using the between strategy
    result['flight_number'] = mid_digits(flight_number)

    if flight_number and flight_number.endswith(tuple(string.ascii_uppercase)):
        # optional operational_suffix is present at end of flight_number,
        # strip it off and put it where it belongs
        result['operational_suffix'] = flight_number[-1]

    return result

def dict_for_company_and_flight_number(
    company_and_flight_number,
    to_addresses = None,
):
    """
    Process string creating company, flight_number, airline_designator, and
    optionally, operational_suffix values.

    :param company_and_flight_number:
    :param to_addresses: optional iterable of to-addresses for resolving
        company value in some cases.
    """
    if to_addresses is None:
        to_addresses = []
    result = {}

    # split company and flight number adding the two keys
    match = company_and_flight_number_re.match(company_and_flight_number)
    if not match:
        raise ValidationError(
            'Unable to split company and flight number in %r',
            company_and_flight_number)
    match_dict = match.groupdict()
    result.update(
        company = match_dict['company'],
        flight_number = match_dict['flight_number'],
    )

    data = dict_for_company(result['company'], to_addresses)
    result.update(data)

    # updates from flight number
    data = dict_for_flight_number(result['flight_number'])
    result.update(data)

    return result
