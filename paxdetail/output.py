from jinja2 import Template

class PAXDetailOutput:
    """
    A `str`-able class meant to behave like
    `lido.message.LIDOWeightBalanceMessage`. This is so that there is access to
    the `schema_data` dict to the filenaming function.
    """

    xml_template = Template("""\
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <transaction>
        <sender>{{ sender }}</sender>
        <created>{{ created.strftime('%Y-%m-%dT%H:%M:%SZ') }}</created>
        <messages>
            <paxDetail>
                <legId>
                    <flight>
                        <fnCarrier>{{ airline_designator }}</fnCarrier>
                        <fnNumber>{{ flight_number }}</fnNumber>
                    </flight>
                    <dayOfOrigin>{{ print_time_gmt.strftime('%Y-%m-%d') }}</dayOfOrigin>
                    <depApSched>{{ origin_iata }}</depApSched>
                    <counter>{{ counter }}</counter>
                </legId>
                <deadloadFlown>
                    <baggageMass>{{ "%.0f" | format(baggage_mass) }}</baggageMass>
                    <cargoMass>{{ "%.0f" | format(cargo_mass) }}</cargoMass>
                    <baggagePieces>{{ uld_count }}</baggagePieces>
                </deadloadFlown>
            </paxDetail>
        </messages>
    </transaction>""")

    def __init__(self, schema_data):
        self.schema_data = schema_data

    def __str__(self):
        return self.xml_template.render(**self.schema_data)


def make_xml(schema_data):
    return PAXDetailOutput(schema_data)
