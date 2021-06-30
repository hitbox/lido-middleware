import re

from units import valid_weight_units_pattern

from extradata import airline_designators

dense_data_line_re = re.compile(
    # flight number
    '(?P<airline_and_flight_number>[A-Z0-9]+)'
    '/'
    # day (number)
    '(?P<day>\d{2})'
    # tail
    '\.(?P<tail>[A-Z0-9]{3,})'
    # dash separated origin-destination (IATA)
    '\.(?P<origin_iata>[A-Z0-9]{3})'
    '\-(?P<destination_iata>[A-Z0-9]{3})')

si_load_re = re.compile(
     'SI LOAD'
     '\s+'
     'GROSS:(?P<gross>\d+)'
     '\s+'
     'NET:(?P<net_weight>\d+)'
     '\s+'
     'ULOAD:(?P<uload>\d+)'
     '\s+'
     'SOB:(?P<souls_onboard>\d+)'
     '\s+'
     'WT:(?P<weights_unit>' + valid_weight_units_pattern + ')'
)

si_load_uld_count_re = re.compile('.*#ULD:\s*(?P<uld_count>\d+)$')

positions_header_re = re.compile(
    '(?P<position>\s+POS\s+)'
    '(?P<destination>DST\s+)'
    '(?P<uldnumber>ULDNUMBER\s+)'
    '(?P<tare>TARE\s+)'
    '(?P<nett>NETT\s+)'
    '(?P<total>TOTAL\s+)'
    '(?P<flag>FLAG\s+)'
    '(?P<vol>VOL\s*)$')
