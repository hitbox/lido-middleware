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

def cleanlines(s):
    """
    Return s with cleaned newlines.
    """
    return '\n'.join(s.splitlines())

def hide(s, char='*'):
    """
    Hide/mask characters of string.
    """
    return ''.join(char for c in s)
