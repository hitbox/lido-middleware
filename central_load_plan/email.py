import re
import textwrap

from jinja2 import Template

from utils import sliding_match

_whitespaceruns_re = re.compile(r'\s+')

# NOTES:
# 1. The big chain of function calls in email_8c.txt template is to remove the
#    duplicated item number from the description, wrap the text to a limit, and
#    finally put the 'Expiration Date:' text on a newline. This comment is here
#    because that template could use some way of simplifying but don't want
#    company specific functions in here.

def clean_remove(substr, text):
    """
    match some `substr` in `text`, removing everything from the beginning of
    `text` to the first space after `substr`.
    """
    # TODO: replace runs of whitespace with one space?
    i = sliding_match(substr, text)
    if i:
        # find first space after substr
        i = text.find(' ', i+len(substr))
        text = text[i:].strip()
    return text

def rfindinsert(substr, text, ins):
    """
    Insert `ins` at position `text.rfind(substr)`.
    """
    i = text.rfind(substr)
    if i == -1:
        return text
    return text[:i] + ins + text[i:]

def fullv1(status, **textwrap_options):
    """
    De-duplicate the item number from the description. Look for an place on a
    newline, the text "Expiration Date:" and everything after it.
    """
    description = clean_remove(status['item'], status['description'])

    items = description.rpartition('Expiration Date:')
    before, expdate, after = items
    if before and expdate and after:
        before = '\n'.join(textwrap.wrap(before, **textwrap_options))
        after = '\n'.join(textwrap.wrap(expdate + after, **textwrap_options))

        if 'subsequent_indent' in textwrap_options:
            subsequent_indent = textwrap_options['subsequent_indent']
        else:
            subsequent_indent = ''

        description = before + '\n' + subsequent_indent + after

    return description

def render(template_path, data):
    """
    Render email body text from airline specific template.
    """
    with open(template_path) as fp:
        template_string = fp.read()
        template = Template(template_string)
        context = dict(
            textwrap = textwrap,
            clean_remove = clean_remove,
            rfindinsert = rfindinsert,
            fullv1 = fullv1,
        )
        context.update(data)
        return template.render(**context)
