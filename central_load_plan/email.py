import re
import textwrap

from jinja2 import Template

from utils import sliding_match

_whitespaceruns_re = re.compile(r'\s+')

def clean_remove(substr, text):
    # replace runs of whitespace with one space
    i = sliding_match(substr, text)
    if i:
        # find first space after substr
        i = text.find(' ', i+len(substr))
        text = text[i:].strip()
    return text

def render(emailconf, data):
    """
    Render email body text from airline specific template.
    """
    template_path = emailconf['template']
    with open(template_path) as fp:
        template_string = fp.read()
        template = Template(template_string)
        context = dict(
            textwrap = textwrap,
            clean_remove = clean_remove,
        )
        context.update(data)
        return template.render(**context)
