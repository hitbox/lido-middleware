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

def getnumkeys(mapping, prefix):
    """
    Return list of keys in mapping that are exactly the prefix or the prefix
    plus numbers.
    """
    values = []
    if prefix in mapping:
        values.append(mapping[prefix])
    for key in mapping:
        if (key.startswith(prefix)
            and key[len(prefix):].isdigit()
        ):
            values.append(mapping[key])
    return values

def hide(s, char='*'):
    """
    Hide/mask characters of string.
    """
    return ''.join(char for c in s)

def printexcept(func):
    """
    Decorate function printing any exceptions.
    """
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
    return wrapper

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

def startfile(filepath):
    """
    Open a file with default application.
    """
    import os
    import platform
    import subprocess
    if platform.system() == 'Darwin':
        # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':
        # Windows
        os.startfile(filepath)
    else:
        # linux variants
        subprocess.call(('xdg-open', filepath))
