from wtforms import SubmitField
from markupsafe import Markup

class AddFieldListEntry(SubmitField):
    """
    A SubmitField that adds a new entry to a FieldList via JavaScript.
    """

    def __init__(self, label=None, fieldlist_id=None, **kwargs):
        """
        fieldlist_id: HTML id of the container of the FieldList entries
        """
        super().__init__(label, **kwargs)
        self.fieldlist_id = fieldlist_id

    def __call__(self, **kwargs):
        # Render normal button
        html = f'<button type="button" id="{self.id}">{self.label.text}</button>'

        # Add JS to clone empty entry
        html += f"""
        <script>
        document.getElementById("{self.id}").addEventListener('click', function() {{
            const container = document.getElementById("{self.fieldlist_id}");
            const index = container.children.length;

            // Find the empty form template
            const template = document.getElementById("{self.fieldlist_id}-template");
            let clone = template.cloneNode(true);
            clone.style.display = 'block';
            clone.removeAttribute('id');

            // Update all input/select names and ids
            clone.querySelectorAll('input, select, textarea').forEach(function(el) {{
                el.name = el.name.replace(/__prefix__/, index);
                el.id = el.id.replace(/__prefix__/, index);
                el.value = '';
            }});

            container.appendChild(clone);
        }});
        </script>
        """
        return Markup(html)
