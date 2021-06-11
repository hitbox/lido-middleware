from datetime import datetime

def taf_filename(fn):
    """
    Return 4-tuple: (None, None, filename datetime, None)
    """
    # TAF: Terminal Aerodrome Forecasts
    # first two and last are unknown to me at this time
    # also this is not used.
    _, _, dtstr, _ = fn.split('.')
    dt = datetime.strptime(dtstr, '%Y%m%dT%H%M%S')
    return (None, None, dt, None)
