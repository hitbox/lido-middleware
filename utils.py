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

def sliding_match(substr, text):
    """
    Slide along `text` looking for the best match of `substr`.
    """
    best = 0
    best_index = None
    i = 0
    while True:
        look = text[i:i+len(substr)]
        nmatch = sum(c1 == c2 for c1, c2 in zip(look, substr))
        if nmatch > best:
            best = nmatch
            best_index = i
        i += 1
        if i + len(substr) >= len(text):
            break
    return best_index
