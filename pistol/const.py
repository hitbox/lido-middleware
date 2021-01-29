VALID_DETAIL_WEIGHT_NAMES = ['OEW', 'Zero Fuel', 'Takeoff', 'Taxi', 'Landing']
VALID_OTHER_WEIGHT_NAMES = ['Ramp Fuel Wt', 'Fuel Wing Wt', 'Fuel Center Wt',
                            'Taxi Fuel Wt', 'Takeoff Fuel', 'PLAN FUEL BURN',
                            'EST FUEL BURN']
VALID_WEIGHT_NAMES = VALID_DETAIL_WEIGHT_NAMES + VALID_OTHER_WEIGHT_NAMES

VALID_CONFIG_NAME_PATTERNS = ['Cargo Wt', 'Main Deck Wt', 'Belly Wt',
                              'Revenue Wt', 'Fwd[A-Z\d/ ]+', 'Aft [A-Z\d/ ]+',
                              'ACM {2,}\d']
