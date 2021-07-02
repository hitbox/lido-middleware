from datetime import datetime

import sable2.schema
import pistol2.schema

class TempPaxDetailSchema:
    """
    This exists to make things work with the current design where a class is
    passed to the run.run func. It just instantiates the "schema" class and
    then calls .load
    """

    def __init__(self, sable_from, pistol_from):
        self.sable_from = sable_from
        self.pistol_from = pistol_from

    def __call__(self):
        return PaxDetailSchema(self.sable_from, self.pistol_from)


class PaxDetailSchema:

    def __init__(self, sable_from, pistol_from):
        self.sable_from = sable_from
        self.pistol_from = pistol_from

    def __call__(self, extract_data):
        from_ = extract_data['message_from'].lower()

        if from_ in self.sable_from:
            # sable
            schema_data = sable2.schema.LoadPlanSchema().load(extract_data)
            baggage_mass_field = 'payload'
            cargo_mass_field = 'net_weight'
            baggage_pieces_field = 'uld_count'

        elif from_ in self.pistol_from:
            # pistol
            schema_data = pistol2.schema.LoadPlanSchema().load(extract_data)
            baggage_mass_field = 'gross_weight'
            cargo_mass_field = 'revenue_weight'
            baggage_pieces_field = 'uld_count'

        else:
            raise ValueError

        result = dict(
            sender = 'LDM2PAX',
            created = datetime.utcnow(),
            counter = 0,
        )

        keep = [
            'airline_designator',
            'flight_number',
            'print_time_gmt',
            'payload',
            'positions',
            'gross_weight_kg',
            'payload_kg',
            'revenue_weight_kg',
            'net_weight_kg',
            'origin_iata',
            'counter',
            baggage_mass_field,
            baggage_pieces_field,
            cargo_mass_field,
        ]
        for key in schema_data:
            if key in keep:
                result[key] = schema_data[key]

        def rename(old, new):
            result[new] = result[old]
            del result[old]

        def safe_rename(old, new):
            if old in result:
                rename(old, new)

        # sable
        safe_rename('net_weight_kg', 'baggage_mass')
        safe_rename('gross_weight_kg', 'cargo_mass')

        # pstl
        safe_rename('revenue_weight_kg', 'baggage_mass')
        safe_rename('payload_kg', 'cargo_mass')

        return result
