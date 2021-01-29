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
