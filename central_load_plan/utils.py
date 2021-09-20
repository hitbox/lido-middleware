from collections import ChainMap

def keyed_sections(cp, prefix, sep='_', func=None):
    """
    Loop configparser sections starting with `prefix + sep`, creating a dict
    keyed on text after `sep` with values of dicts of that section. If a
    section named `prefix` exists it will be used as a base dict for the more
    specific keyed sections.

    (ignore spaces between in section names)
    [prefix]
    c = 5

    [prefix sep key1]
    a = 1

    [prefix sep key2]
    b = 2

    ...

    {'key1': {'a': '1', 'c': '5'}, 'key2': {'b': '2', 'c': '5'}, ...}

    :param cp: a ConfigParser instance
    :param prefix: first part of section name
    :param sep: separator string between first and last part
    :param func: a callable called on the dict values, useful for coercing types
    """
    if prefix in cp:
        base = cp[prefix]
    else:
        base = {}

    if func is None:
        func = lambda x: x

    result = {
        secname.partition(sep)[2]: func(dict(ChainMap(cp[secname], base)))
        for secname in cp if secname.startswith(prefix + sep)
    }
    return result
