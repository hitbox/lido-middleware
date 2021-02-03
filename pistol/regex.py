import re

from units import valid_weight_units_pattern

from .const import VALID_CONFIG_NAME_PATTERNS
from .const import VALID_DETAIL_WEIGHT_NAMES
from .const import VALID_OTHER_WEIGHT_NAMES

debrief_line_re = re.compile('^-------- Debrief --------')
end_line_re = re.compile('^-------- end ---------')
tape_line_re = re.compile('^-------- tape --------')
main_deck_header = re.compile(
    '^\s{4,}Main Deck \d+ (%s)' % valid_weight_units_pattern)
pistol_metadata_re = re.compile(
    'ver:(?P<pistol_version>[A-Z_0-9\.]+)'
    ' computer:(?P<computer>[A-Za-z0-9\-]+)'
    ' Print time:'
    ' (?P<print_time_local>\d{2}/\d{2}/\d{2} \d{4}) LCL'
    '  (?P<print_time_gmt>\d{2}/\d{2}/\d{2} \d{4}) GMT'
)
space_run = re.compile(' +')

destination_iata_or_icao_pattern = '[A-Z0-9]{3,4}'

ad_line_re = re.compile(
     '^AD'
     '(?P<ad_unknown1>Update|\d{4}|0\.:\d\d)' # weird unknown data.
     '/'
     '(?P<ad_unknown2>Update|\d{4}|0\.:\d\d|N/A)' # another weird unknown field.
     '\.'
     'EA0000' # constant AFAIK
     '\.'
    f'(?P<destination_iata_or_icao>{destination_iata_or_icao_pattern})'
     '$')

souls_onboard_re = re.compile('^SOB \d{1,}$')

# dense lines patterns are the same with different group names and one unique
# name each.
dense_line_re1 = re.compile(
    '^'
    '(?P<company_and_flight_number1>[A-Z0-9]+)'
    '/'
    '(?P<day1>[0-9]+)'
    '\.'
    '(?P<aircraft_registration1>[A-Z0-9]+)'
    '\.'
    '(?P<origin_iata_or_icao>[A-Z ]+)$')

dense_line_re2 = re.compile(
    '^'
    '(?P<company_and_flight_number2>[A-Z0-9]+)'
    '/'
    '(?P<day2>[0-9]+)'
    '\.'
    '(?P<aircraft_registration2>[A-Z0-9]+)'
    '\.'
    '(?P<color_code>[A-Za-z ]+)$')

si_line_re = re.compile(
     '^SI ALL WGT ARE ' # preamble
    f'(?P<all_weights_unit>{valid_weight_units_pattern})$')

position_line_nil_re = re.compile('^\-(?P<position>[A-Z0-9]+).NIL$')

position_line_re = re.compile(
     '^\-' # starts with dash
     '(?P<position>[A-Z0-9]+)'
     '/'
     '(?P<unit_load_device>[A-Z0-9 ]+)'
     '/'
    f'(?P<destination_iata_or_icao>{destination_iata_or_icao_pattern}| )' # or space
     '/'
    f'(?P<weight>\d+)(?P<weight_unit>{valid_weight_units_pattern})'
     '/'
     '(?P<building>[A-Z0-9]+)'
     '$')

weight_and_unit_re = re.compile(
    '(?P<weight>\d+)(?P<weight_unit>%s)' % valid_weight_units_pattern)

valid_config_name_pattern = '|'.join(VALID_CONFIG_NAME_PATTERNS)
valid_detail_weight_name_pattern = '|'.join(VALID_DETAIL_WEIGHT_NAMES)
valid_other_weight_names_pattern = '|'.join(VALID_OTHER_WEIGHT_NAMES)
valid_weight_name_pattern = '|'.join(VALID_DETAIL_WEIGHT_NAMES + VALID_OTHER_WEIGHT_NAMES)

config_line_re = re.compile(
    '(?P<name>%s) +(?P<value>[\d/]+$)'
    % valid_config_name_pattern)

detail_weight_line_re = re.compile(
    '(?P<name>%s) +(?P<weight>\d+) +(?P<forward>[\d\.]+|N/A)'
    ' +(?P<cg_percent_mac>[\d\.]+|N/A) +(?P<aft>[\d\.]+|N/A)'
    % valid_detail_weight_name_pattern)

other_weight_line_re = re.compile(
    '^(?P<name>%s) +(?P<weight>\d+)'
    '($|\ +)' # either the end of the string or some spaces
    % valid_other_weight_names_pattern)
