import xml.etree.ElementTree as ET

from jinja2 import Template

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
                <baggageMass>{{ "%.1f" | format(baggage_mass) }}</baggageMass>
                <cargoMass>{{ "%.1f" | format(cargo_mass) }}</cargoMass>
                <baggagePieces>{{ uld_count }}</baggagePieces>
            </deadloadFlown>
        </paxDetail>
    </messages>
</transaction>""")

def make_xml(schema_data):
    return xml_template.render(**schema_data)
