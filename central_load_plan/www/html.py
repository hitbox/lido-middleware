from markupsafe import Markup

def render_object(obj, html=None):
    if html is None:
        html = []
    if isinstance(obj, dict):
        html.append('<dl>')
        for key, value in obj.items():
            html.append(f'<dt>{key}</dt>')
            html.append(f'<dd>{render_object(value, html=html)}</dd>')
        html.append('</dl>')
    elif isinstance(obj, list):
        html.append(f'<ul>')
        for item in obj:
            html.append(f'<li>{render_object(item, html=html)}</li>')
        html.append(f'</ul>')
    else:
        return str(obj)
    return Markup(''.join(html))
