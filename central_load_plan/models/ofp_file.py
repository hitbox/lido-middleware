import uuid

import sqlalchemy as sa

from .clp_base import CLPBase

class OFPFile(CLPBase):
    """
    OFP XML file scraped for data.
    """

    __tablename__ = 'ofp_file'

    id = sa.Column(sa.Uuid, primary_key=True, default=uuid.uuid4)

    original_path = sa.Column(sa.String, nullable=True)

    archive_path = sa.Column(
        sa.String,
        nullable=True,
        info = {
            'help': 'Existing path.',
        },
    )

    @property
    def display_path(self):
        if self.original_path:
            return self.original_path
        else:
            return self.archive_path

    flight_plan_id = sa.Column(sa.String, nullable=False)

    leg_departure_date_utc = sa.Column(sa.DateTime(timezone=True), nullable=False)

    flight_origin_date = sa.Column(sa.Date)

    version_number = sa.Column(sa.String)

    flight_number = sa.Column(sa.Integer)

    flight_identifier = sa.Column(sa.String)

    airline_iata_code = sa.Column(sa.String)

    origin_iata = sa.Column(sa.String)

    destination_iata = sa.Column(sa.String)

    aircraft_registration = sa.Column(sa.String)

    estimated_block_time = sa.Column(sa.Time)

    estimated_time_enroute = sa.Column(sa.Time)

    scheduled_departure_time = sa.Column(sa.DateTime(timezone=True))

    estimated_departure_time = sa.Column(sa.DateTime(timezone=True))

    planned_payload = sa.Column(sa.Integer)

    planned_payload_unit = sa.Column(sa.String)

    ramp_fuel = sa.Column(sa.Integer)

    ramp_fuel_unit = sa.Column(sa.String)

    fuel_burn = sa.Column(sa.Integer)

    fuel_burn_unit = sa.Column(sa.String)

    taxi_fuel = sa.Column(sa.Integer)

    taxi_fuel_unit = sa.Column(sa.String)

    takeoff_fuel = sa.Column(sa.Integer)

    takeoff_fuel_unit = sa.Column(sa.String)

    landing_fuel = sa.Column(sa.Integer)

    landing_fuel_unit = sa.Column(sa.String)

    ballast_fuel = sa.Column(sa.Integer)

    ballast_fuel_unit = sa.Column(sa.String)

    mzfw = sa.Column(sa.Integer)

    mzfw_unit = sa.Column(sa.String)

    mtow = sa.Column(sa.Integer)

    mtow_unit = sa.Column(sa.String)

    mldg = sa.Column(sa.Integer)

    mldg_unit = sa.Column(sa.String)

    dow = sa.Column(sa.Integer)

    dow_unit = sa.Column(sa.String)

    aircraft_equipment_status_list = sa.orm.relationship(
        'AircraftEquipmentStatus',
        back_populates = 'ofp_files',
    )

    crewmembers = sa.orm.relationship(
        'CrewMember',
        back_populates = 'ofp_files',
    )

    jobs = sa.orm.relationship(
        'Job',
        back_populates = 'ofp_file',
    )


class AircraftEquipmentStatus(CLPBase):

    __tablename__ = 'aircraft_equipment_status'

    id = sa.Column(sa.Uuid, primary_key=True, default=uuid.uuid4)

    item = sa.Column(sa.String)

    description = sa.Column(sa.String)

    ofp_file_id = sa.Column(sa.ForeignKey('ofp_file.id'))

    ofp_files = sa.orm.relationship(
        'OFPFile',
        back_populates = 'aircraft_equipment_status_list',
    )


class CrewMember(CLPBase):

    __tablename__ = 'crew_member'

    id = sa.Column(sa.Uuid, primary_key=True, default=uuid.uuid4)

    ofp_file_id = sa.Column(sa.ForeignKey('ofp_file.id'))

    ofp_files = sa.orm.relationship(
        'OFPFile',
        back_populates = 'crewmembers',
    )

    first_name = sa.Column(sa.String)

    last_name = sa.Column(sa.String)

    employee_number = sa.Column(sa.String)

    seat = sa.Column(sa.String)

    source = sa.Column(sa.String)

    seat_order = sa.Column(sa.Integer)
