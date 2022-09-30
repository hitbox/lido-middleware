import datetime
import os
import shutil
import sys
import traceback

from collections import ChainMap

from .constants import EXCEPTION_DATETIME_FMT

def move_for_exception(source, move_to, e):
    """
    Move `source` to destination `move_to` with the current datetime put in the
    filename. Write another file next to it in the destination, with the
    exception `e` in it.
    """
    # capture now for both files
    now = datetime.datetime.now()
    # get just filename part
    source_base = os.path.basename(source)
    # split to insert now
    base_root, base_ext = os.path.splitext(source_base)
    # combine base filename, now and extension
    dest_fn = ''.join([
        base_root,
        now.strftime(EXCEPTION_DATETIME_FMT),
        base_ext,
    ])
    # combine with exception directory
    dest_path = os.path.join(move_to, dest_fn)

    # should be safe with a filename with a full datetime in it.
    shutil.move(source, dest_path)

    # write stacktrace
    dest_fn = ''.join([
        base_root,
        now.strftime(EXCEPTION_DATETIME_FMT),
        '.STACKTRACE.txt',
        base_ext,
    ])
    dest_path = os.path.join(move_to, dest_fn)
    with open(dest_path, 'w') as stacktrace_fp:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        stack_string = ''.join(lines)
        stacktrace_fp.write(stack_string)
        stacktrace_fp.write(str(e))

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

    def keyvalue(secname):
        key = secname[len(prefix):].partition(sep)[2]
        value = func(dict(ChainMap(cp[secname], base)))
        return (key, value)

    result = dict(
        keyvalue(secname) for secname in cp
        if secname.startswith(prefix + sep)
    )
    return result
