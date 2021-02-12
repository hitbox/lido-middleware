import re

dense1_re = re.compile(
    '(?P<unknown1>[A-Z]+)'
    '/'
    '(?P<aircraft_registration>[A-Z0-9]+)'
    '/'
    '(?P<airline_and_flight_number>[A-Z0-9]+)')

loadsheet_re = re.compile(
    'LOADSHEET'
    ' {3,}' # bunch of spaces
    'FINAL (?P<loadsheet_final_number>\d\d)')

dense2_re = re.compile(
    '(?P<origin_iata>[A-Z]{3})'
    ' {1,}'
    '(?P<destination_iata>[A-Z]{3})'
    ' {2,}'
    '(?P<airline_and_flight_number2>[A-Z0-9]{5,})'
    '/'
    '(?P<day>\d{1,})'
    ' {2,}'
    '(?P<aircraft_registration2>[A-Z0-9]+)')

dense3_re = re.compile(
    '(?P<unknown2>[A-Z0-9]{3,})'
    ' {4,}'
    '(?P<unknown3>\d/\d/\d)'
    ' {4,}'
    '(?P<date>\d{2}[A-Z]{3}\d{2})')

_weight_name_and_kg_pattern = (
    '(?P<weight_name>[A-Z][A-Z ]+)'
    ' {2,}'
    '(?P<weight_kg>\d{3,})'
    # after this number there is sometimes a letter. think L or R. do we need
    # this? ignoring for now.
    )

weight_re = re.compile(_weight_name_and_kg_pattern)

weight_with_max_re = re.compile(
    _weight_name_and_kg_pattern
    + ' {2,}'
    'MAX (?P<max_kg>\d{3,})')

weight_position_re = re.compile(
    '(?P<weight>\d+)(?P<position>\.[A-Z0-9]+)?')
