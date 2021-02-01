def _resolve(name):
    """
    Resolve a dotted name to a global object.
    """
    # copied from Python 3.8 logging.config
    name = name.split('.')
    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used = used + '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)
    return found
