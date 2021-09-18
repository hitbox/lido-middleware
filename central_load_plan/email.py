import textwrap

from jinja2 import Template

def render(emailconf, data):
    """
    Render email body text from airline specific template.
    """
    template_path = emailconf['template']
    with open(template_path) as fp:
        template_string = fp.read()
        template = Template(template_string)
        context = dict(textwrap=textwrap)
        context.update(data)
        return template.render(**context)
