import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base

class Base:

    def __repr__(self):
        return (f'{self.__class__.__name__}(%s)'
                % ', '.join(f'{k}={v!r}' for k, v in self.__dict__.items()))


Base = declarative_base(cls=Base)

class Position(Base):
    """
    Container / Pallet Distribution item.
    """

    __tablename__ = 'positions'

    loadplan_id = sa.Column(sa.Integer, sa.ForeignKey('loadplans.id'))

    id = sa.Column(sa.Integer, primary_key=True)
    position = sa.Column(sa.String)
    unit_load_device = sa.Column(sa.String)
    destination = sa.Column(sa.String)
    weight = sa.Column(sa.Integer)
    weight_unit = sa.Column(sa.String)
    building = sa.Column(sa.String)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.position == other.position
            and self.unit_load_device == other.unit_load_device
            and self.destination == other.destination
            and self.weight == other.weight
            and self.weight_unit == other.weight_unit
            and self.building == other.building)


class Weight(Base):
    """
    Weight information from pstl message report.
    """

    __tablename__ = 'weights'

    loadplan_id = sa.Column(sa.Integer, sa.ForeignKey('loadplans.id'))

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    weight = sa.Column(sa.Integer)
    forward = sa.Column(sa.Float)
    cg_percent_mac = sa.Column(sa.Float)
    aft = sa.Column(sa.Float)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.name == other.name
            and self.weight == other.weight
            and self.forward == other.forward
            and self.aft == other.aft
            and self.cg_percent_mac == other.cg_percent_mac)


class AircraftConfig(Base):
    """
    Aircraft configuration information from pstl message report.
    """

    __tablename__ = 'aircraftconfigs'

    loadplan_id = sa.Column(sa.Integer, sa.ForeignKey('loadplans.id'))

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    value = sa.Column(sa.String)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.name == other.name
            and self.value == other.value)


class LoadPlan(Base):
    """
    Load plan data as from the text load plan messages.
    """

    __tablename__ = 'loadplans'

    id = sa.Column(sa.Integer, primary_key=True)
    load_planner = sa.Column(sa.String)
    company = sa.Column(sa.String)
    flight_number = sa.Column(sa.String)
    aircraft_registration = sa.Column(sa.String)
    actual_departure_time = sa.Column(sa.Time)
    origin_station = sa.Column(sa.String)
    destination_station = sa.Column(sa.String)
    souls_onboard = sa.Column(sa.Integer)
    color_code = sa.Column(sa.String)
    # sqlalchemy_utils.ChoiceType:
    all_weights_unit = sa.Column(sa.String)
    pistol_version = sa.Column(sa.String)
    computer = sa.Column(sa.String)
    print_time_local = sa.Column(sa.DateTime)
    print_time_gmt = sa.Column(sa.DateTime)

    positions = sa.orm.relationship('loadplan.Position')
    weights = sa.orm.relationship('loadplan.Weight')
    aircraft_configurations = sa.orm.relationship('loadplan.AircraftConfig')
