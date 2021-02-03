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
    f'WT:(?P<weights_unit>{valid_weight_units_pattern})')

header_re = re.compile(
    '(?P<position>\s+POS)'
    '(?P<destination>\s+DST)'
    '(?P<uldnumber>\s+ULDNUMBER)'
    '(?P<tare>\s+TARE)'
    '(?P<nett>\s+NETT)'
    '(?P<total>\s+TOTAL)'
    '(?P<flag>\s+FLAG)'
    '(?P<vol>\s+VOL)$')
