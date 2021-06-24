class ToAddrAirlineMapError(Exception):
    pass


_tomap = {
    'atiflc': '8C',
    'flight.control': 'GB',
}

def airline_from_toaddr(toaddrs):
    matches = []
    for addr in toaddrs:
        addr = addr.lower()
        for prefix, airline_code in _tomap.items():
            if addr.startswith(prefix):
                matches.append(airline_code)
                break

    nmatches = len(matches)
    if nmatches != 1:
        if nmatches == 0:
            raise ToAddrAirlineMapError('No airline matches for to addresses')
        else:
            raise ToAddrAirlineMapError('More than one match for to addresses')

    return matches[0]
