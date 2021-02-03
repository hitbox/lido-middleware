{
    'flight_number': '987',
    'company': 'ABX',
    'airline_designator': 'GB',
    'day': 30,
    'tail': 'N123BB',
    'origin_iata': 'AAA',
    'destination_iata': 'BBB',
    'gross': 12345,
    'net_weight': 67890,
    'uload': 1234,
    'souls_onboard': 5,
    'all_weights_unit': 'KG',

    # constants
    'planning_status': '04',
    'duplicate_number': '1',
    'revision_number': '00',
    'operational_suffix': ' ',
    'pax_baggage_indicator': 'N',
    'cargo_mail_indicator': 'N',
    'transit_load_indicator': 'N',
    'tail_tank_indicator': ' ',
    'estimated_pax': 0,
    'dry_operating_index': None,
    'estimated_pax_class_one': None,
    'estimated_pax_class_two': None,
    'estimated_pax_class_three': None,

    'positions': [
        {'destination_iata': 'BBB', 'flag': '*DGRORDGTWLATWPXNCYORGCG',
         'net_weight': 1171, 'position': 'A1', 'tare': 111, 'total': 1282,
         'unit_load_device': 'ABC0123ZZZ', 'volume': '100'},
        {'destination_iata': None, 'flag': None, 'net_weight': 0, 'position': 'A2',
         'tare': 0, 'total': 0, 'unit_load_device': 'VOID', 'volume': '0'},
        {'destination_iata': None, 'flag': None, 'net_weight': None, 'position':
         'A3', 'tare': None, 'total': None, 'unit_load_device': 'VOID',
         'volume': None},
        {'destination_iata': 'CCC', 'flag': 'CVGHUBMIPCNYORGBAH(SPX)',
         'net_weight': 1234, 'position': '3L', 'tare': 258, 'total': 1492,
         'unit_load_device': 'DEF4567ZZZ', 'volume': '100'}
    ],
}
