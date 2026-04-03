from wtforms import Form

class OFPFileFilterForm(Form):

    airline_iata_code = SelectField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.airline_iata_code.choices = db.session.scalars(db.select(OFPFile.airline_iata_code).distinct()).all()
