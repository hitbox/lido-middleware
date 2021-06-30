import sable2.schema
import pistol2.schema

class SchemaDelegator:

    def __init__(self, sable_from, pistol_from):
        self.sable_from = sable_from
        self.pistol_from = pistol_from

    def __call__(self, data):
        """
        delegate schema to sable2, pistol2, etc.
        """

        from_ = data['message_from'].lower()

        if from_ in self.sable_from:
            schema = sable2.schema.LoadPlanSchema()
        elif from_ in self.pistol_from:
            schema = pistol2.schema.LoadPlanSchema()
        else:
            raise ValueError
        return schema.load(data)
