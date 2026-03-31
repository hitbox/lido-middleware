from datetime import datetime
from datetime import time

import sqlalchemy as sa

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.hybrid import hybrid_property

class LSYBase(DeclarativeBase):

    __bind_key__ = 'lsyrept'


class FilterMixin:

    @classmethod
    def filter_for_data(cls, data):
        flight_no = data['flight_number']
        if cls == Duty:
            flight_no = str(data['flight_number'])
        return sa.and_(
            cls.airline == data['airline_iata_code'],
            cls.day_of_origin == datetime.combine(data['flight_origin_date'], time()),
            cls.flight_no == flight_no,
            cls.airport_c_is_dep == data['origin_iata'],
            cls.departure_date_scd == data['scheduled_departure_time'].date(),
            # departure_time_scd is stored as CHAR(4)
            cls.departure_time_scd == data['scheduled_departure_time'].strftime('%H%M'),
        )


class TrimmedNameMixin:

    @classmethod
    def trimmed_name(cls):
        return sa.func.trim(cls.name)

    @classmethod
    def trimmed_first_name(cls):
        return sa.func.trim(cls.first_name)

    @classmethod
    def trimmed_employee_no(cls):
        return sa.func.trim(cls.employee_no)



class ChainItemDaily(LSYBase):
    __tablename__ = 'CHAIN_ITEM_DAILY'

    chain_daily_uno = sa.Column('CHAIN_DAILY_UNO', sa.Integer, primary_key=True, nullable=False)
    item_daily_uno = sa.Column('ITEM_DAILY_UNO', sa.Integer, primary_key=True, nullable=False)

    ci_date_cockpit = sa.Column('CI_DATE_COCKPIT', sa.Date, nullable=False)
    ci_time_cockpit = sa.Column('CI_TIME_COCKPIT', sa.String(4), nullable=False)

    co_date_cockpit = sa.Column('CO_DATE_COCKPIT', sa.Date, nullable=False)
    co_time_cockpit = sa.Column('CO_TIME_COCKPIT', sa.String(4), nullable=False)

    ref_date_ci_cockpt = sa.Column('REF_DATE_CI_COCKPT', sa.Date, nullable=False)
    ref_time_ci_cockpt = sa.Column('REF_TIME_CI_COCKPT', sa.String(4), nullable=False)

    ci_date_cabin = sa.Column('CI_DATE_CABIN', sa.Date, nullable=False)
    ci_time_cabin = sa.Column('CI_TIME_CABIN', sa.String(4), nullable=False)

    co_date_cabin = sa.Column('CO_DATE_CABIN', sa.Date, nullable=False)
    co_time_cabin = sa.Column('CO_TIME_CABIN', sa.String(4), nullable=False)

    ref_date_ci_cabin = sa.Column('REF_DATE_CI_CABIN', sa.Date, nullable=False)
    ref_time_ci_cabin = sa.Column('REF_TIME_CI_CABIN', sa.String(4), nullable=False)


class CrewMember(TrimmedNameMixin, LSYBase):
    __tablename__ = "CREW_MEMBER"

    tlc = sa.Column(sa.String(8), primary_key=True, nullable=False)

    name = sa.Column(sa.String(30), nullable=False)
    middle_name = sa.Column(sa.String(30), nullable=False)
    first_name = sa.Column(sa.String(30), nullable=False)
    title = sa.Column(sa.String(20), nullable=False)
    birth_name = sa.Column(sa.String(100), nullable=False)
    national_name = sa.Column(sa.String(160), nullable=False)

    employee_no = sa.Column(sa.String(12), nullable=False)
    personal_id = sa.Column(sa.String(20), nullable=False)

    seniority = sa.Column(sa.Integer, nullable=False)
    nationality = sa.Column(sa.String(3), nullable=False)
    sex = sa.Column(sa.String(1), nullable=False)

    birth_date = sa.Column(sa.Date, nullable=False)
    employment_begin_dt = sa.Column(sa.DateTime, nullable=False)
    employment_end_dt = sa.Column(sa.DateTime, nullable=False)

    is_smoker = sa.Column(sa.String(1), nullable=False)

    suspension_begin_dt = sa.Column(sa.DateTime, nullable=False)
    suspension_end_dt = sa.Column(sa.DateTime, nullable=False)
    suspension_reason = sa.Column(sa.String(15), nullable=False)

    claims_begin = sa.Column(sa.Date, nullable=False)

    off_rest_last_year = sa.Column(sa.Numeric(6, 2), nullable=False)
    off_cl_this_year = sa.Column(sa.Numeric(6, 2), nullable=False)
    off_cl_next_year = sa.Column(sa.Numeric(6, 2), nullable=False)

    vac_rest_last_year = sa.Column(sa.Integer, nullable=False)
    vac_cl_this_year = sa.Column(sa.Integer, nullable=False)
    vac_cl_next_year = sa.Column(sa.Integer, nullable=False)

    vac_mod_this_year = sa.Column(sa.Integer, nullable=False)
    vac_mod_reason = sa.Column(sa.String(32), nullable=False)

    priority = sa.Column(sa.Integer, nullable=False)

    hrs_eq_dist_ros = sa.Column(sa.Integer, nullable=False)
    hrs_eq_dist_ctl = sa.Column(sa.Integer, nullable=False)

    equivalent_fh_ros = sa.Column(sa.Integer, nullable=False)
    equivalent_fh_ctl = sa.Column(sa.Integer, nullable=False)

    hrs_eq_dist_ros_yr = sa.Column(sa.Integer, nullable=False)
    hrs_eq_dist_ctl_yr = sa.Column(sa.Integer, nullable=False)

    fh_per_year_ros_sp = sa.Column(sa.Integer, nullable=False)
    fh_per_year_ctl_sp = sa.Column(sa.Integer, nullable=False)

    remark = sa.Column(sa.String(254), nullable=False)

    next_day_for_nas = sa.Column(sa.Date, nullable=False)

    cc_number = sa.Column(sa.String(18), nullable=False)
    new_cc_begin_date = sa.Column(sa.Date, nullable=False)
    old_cc_number = sa.Column(sa.String(18), nullable=False)

    place_of_birth = sa.Column(sa.String(25), nullable=False)
    state_of_birth = sa.Column(sa.String(25), nullable=False)
    country_of_birth = sa.Column(sa.String(40), nullable=False)

    off_pts = sa.Column(sa.Numeric(7, 3), nullable=False)
    night_stop_pts = sa.Column(sa.Numeric(7, 3), nullable=False)

    last_update_ctl = sa.Column(sa.Integer, nullable=False)
    last_update_ros = sa.Column(sa.Integer, nullable=False)
    last_update_qar = sa.Column(sa.Integer, nullable=False)

    destination_idpl = sa.Column(sa.String(1), nullable=False)

    off_mod_this_year = sa.Column(sa.Numeric(6, 2), nullable=False)
    off_mod_reason = sa.Column(sa.String(32), nullable=False)

    pregnancy_begin = sa.Column(sa.Date, nullable=False)
    est_pregnancy_end = sa.Column(sa.Date, nullable=False)

    med_restriction = sa.Column(sa.String(15), nullable=False)
    med_restr_begin_dt = sa.Column(sa.DateTime, nullable=False)
    med_restr_end_dt = sa.Column(sa.DateTime, nullable=False)

    active_end_date = sa.Column(sa.Date, nullable=False)
    active_end_time = sa.Column(sa.String(4), nullable=False)

    next_monthly_concl = sa.Column(sa.Date, nullable=False)

    meal_preference = sa.Column(sa.String(1), nullable=False)
    partner_tlc = sa.Column(sa.String(8), nullable=False)

    life_rad_exposure = sa.Column(sa.Integer, nullable=False)

    vac_awd_begin_date = sa.Column(sa.Date, nullable=False)
    vac_changes_notified_before = sa.Column(sa.Date, nullable=False)


class Duty(FilterMixin, LSYBase):
    __tablename__ = "DUTY"

    tlc = sa.Column("TLC", sa.String(8), primary_key=True, nullable=False)
    begin_date = sa.Column("BEGIN_DATE", sa.Date, primary_key=True, nullable=False)
    begin_time = sa.Column("BEGIN_TIME", sa.String(4), primary_key=True, nullable=False)

    code = sa.Column("CODE", sa.String(9), nullable=False)

    end_date = sa.Column("END_DATE", sa.Date, nullable=False)
    end_time = sa.Column("END_TIME", sa.String(4), nullable=False)

    assign_state = sa.Column("ASSIGN_STATE", sa.Integer, nullable=False)
    type_ = sa.Column("TYPE", sa.String(1), nullable=False)

    chain_daily_uno = sa.Column("CHAIN_DAILY_UNO", sa.Integer, nullable=False)
    type_of_assignment = sa.Column("TYPE_OF_ASSIGNMENT", sa.String(1), nullable=False)
    changes_tr_state = sa.Column("CHANGES_TR_STATE", sa.String(1), nullable=False)
    is_trainer = sa.Column("IS_TRAINER", sa.String(1), nullable=False)

    assigned_rank = sa.Column("ASSIGNED_RANK", sa.Integer, nullable=False)
    equivalent_fh = sa.Column("EQUIVALENT_FH", sa.Integer, nullable=False)
    duty_time = sa.Column("DUTY_TIME", sa.Integer, nullable=False)

    airport_c_is_dep = sa.Column("AIRPORT_C_IS_DEP", sa.String(3), nullable=False)
    airport_c_is_dest = sa.Column("AIRPORT_C_IS_DEST", sa.String(3), nullable=False)

    dep_gate = sa.Column("DEP_GATE", sa.String(6), nullable=False)
    arr_gate = sa.Column("ARR_GATE", sa.String(6), nullable=False)

    dep_terminal = sa.Column("DEP_TERMINAL", sa.String(2), nullable=False)
    arr_terminal = sa.Column("ARR_TERMINAL", sa.String(2), nullable=False)

    day_of_origin = sa.Column("DAY_OF_ORIGIN", sa.Date, nullable=False)

    airline = sa.Column("AIRLINE", sa.String(3), nullable=False)
    flight_no = sa.Column("FLIGHT_NO", sa.String(4), nullable=False)
    suffix = sa.Column("SUFFIX", sa.String(1), nullable=False)

    ci_date = sa.Column("CI_DATE", sa.Date, nullable=False)
    ci_time = sa.Column("CI_TIME", sa.String(4), nullable=False)

    co_date = sa.Column("CO_DATE", sa.Date, nullable=False)
    co_time = sa.Column("CO_TIME", sa.String(4), nullable=False)

    departure_date_scd = sa.Column("DEPARTURE_DATE_SCD", sa.Date, nullable=False)
    departure_time_scd = sa.Column("DEPARTURE_TIME_SCD", sa.String(4), nullable=False)

    arrival_date_scd = sa.Column("ARRIVAL_DATE_SCD", sa.Date, nullable=False)
    arrival_time_scd = sa.Column("ARRIVAL_TIME_SCD", sa.String(4), nullable=False)

    username = sa.Column("USERNAME", sa.String(8), nullable=False)

    change_date = sa.Column("CHANGE_DATE", sa.Date, nullable=False)
    change_time = sa.Column("CHANGE_TIME", sa.String(4), nullable=False)

    counter = sa.Column("COUNTER", sa.Integer, nullable=False)
    modification_value = sa.Column("MODIFICATION_VALUE", sa.Integer, nullable=False)

    swap_offer_item_uno = sa.Column("SWAP_OFFER_ITEM_UNO", sa.Integer, nullable=False)
    vacation_request_uno = sa.Column("VACATION_REQUEST_UNO", sa.Integer, nullable=False)

    location_code = sa.Column("LOCATION_CODE", sa.String(9), nullable=False)
    crm_request_uno = sa.Column("CRM_REQUEST_UNO", sa.Integer, nullable=False)

    ac_logical_no = sa.Column("AC_LOGICAL_NO", sa.Integer, nullable=False)
    ac_owner = sa.Column("AC_OWNER", sa.String(3), nullable=False)
    ac_subtype = sa.Column("AC_SUBTYPE", sa.String(3), nullable=False)

    registration = sa.Column("REGISTRATION", sa.String(10), nullable=False)

    @hybrid_property
    def is_deadhead(self):
        return self.type_ == 'F'

    @classmethod
    def seat_case(cls, is_leg):
        return sa.case(
            (sa.and_(is_leg, cls.assigned_rank == 0), 'PIC'),
            (sa.and_(is_leg, cls.assigned_rank == 1), 'SIC'),
            (sa.and_(is_leg, cls.assigned_rank == 2), 'IRO'),
            (sa.and_(is_leg, cls.assigned_rank == 3), 'CP'),
            (sa.and_(is_leg, cls.assigned_rank == 5), 'FA'),
            else_ = 'ACM',
        )

    @classmethod
    def seat_order_case(cls, is_leg, is_deadhead):
        return sa.case(
            (is_leg, cls.assigned_rank),
            (is_deadhead, 99),
        )


class ItemDaily(FilterMixin, LSYBase):
    __tablename__ = "ITEM_DAILY"

    uno = sa.Column("UNO", sa.Integer, primary_key=True, nullable=False)

    ac_type_code = sa.Column("AC_TYPE_CODE", sa.String(4), nullable=False)
    code = sa.Column("CODE", sa.String(9), nullable=False)
    type_ = sa.Column("TYPE", sa.String(1), nullable=False)

    day_of_origin = sa.Column("DAY_OF_ORIGIN", sa.Date, nullable=False)
    counter = sa.Column("COUNTER", sa.Integer, nullable=False)

    airline = sa.Column("AIRLINE", sa.String(3), nullable=False)
    flight_no = sa.Column("FLIGHT_NO", sa.Integer, nullable=False)

    ac_subtype = sa.Column("AC_SUBTYPE", sa.String(3), nullable=False)
    suffix = sa.Column("SUFFIX", sa.String(1), nullable=False)

    area_code = sa.Column("AREA_CODE", sa.String(3), nullable=False)
    crit_exercise_aps = sa.Column("CRIT_EXERCISE_APS", sa.String(39), nullable=False)

    airport_c_is_dep = sa.Column("AIRPORT_C_IS_DEP", sa.String(3), nullable=False)
    airport_c_is_dest = sa.Column("AIRPORT_C_IS_DEST", sa.String(3), nullable=False)

    dep_gate = sa.Column("DEP_GATE", sa.String(6), nullable=False)
    arr_gate = sa.Column("ARR_GATE", sa.String(6), nullable=False)

    dep_terminal = sa.Column("DEP_TERMINAL", sa.String(2), nullable=False)
    arr_terminal = sa.Column("ARR_TERMINAL", sa.String(2), nullable=False)

    departure_date = sa.Column("DEPARTURE_DATE", sa.Date, nullable=False)
    departure_time = sa.Column("DEPARTURE_TIME", sa.String(4), nullable=False)

    arrival_date = sa.Column("ARRIVAL_DATE", sa.Date, nullable=False)
    arrival_time = sa.Column("ARRIVAL_TIME", sa.String(4), nullable=False)

    departure_date_scd = sa.Column("DEPARTURE_DATE_SCD", sa.Date, nullable=False)
    departure_time_scd = sa.Column("DEPARTURE_TIME_SCD", sa.String(4), nullable=False)

    arrival_date_scd = sa.Column("ARRIVAL_DATE_SCD", sa.Date, nullable=False)
    arrival_time_scd = sa.Column("ARRIVAL_TIME_SCD", sa.String(4), nullable=False)

    pushback_date = sa.Column("PUSHBACK_DATE", sa.Date, nullable=False)
    pushback_time = sa.Column("PUSHBACK_TIME", sa.String(4), nullable=False)

    equivalent_fh = sa.Column("EQUIVALENT_FH", sa.Integer, nullable=False)

    no_fd_0 = sa.Column("NO_FD_0", sa.Integer, nullable=False)
    no_fd_1 = sa.Column("NO_FD_1", sa.Integer, nullable=False)
    no_fd_2 = sa.Column("NO_FD_2", sa.Integer, nullable=False)
    no_fd_3 = sa.Column("NO_FD_3", sa.Integer, nullable=False)
    no_fd_4 = sa.Column("NO_FD_4", sa.Integer, nullable=False)

    no_ca_0 = sa.Column("NO_CA_0", sa.Integer, nullable=False)
    no_ca_1 = sa.Column("NO_CA_1", sa.Integer, nullable=False)
    no_ca_2 = sa.Column("NO_CA_2", sa.Integer, nullable=False)
    no_ca_3 = sa.Column("NO_CA_3", sa.Integer, nullable=False)
    no_ca_4 = sa.Column("NO_CA_4", sa.Integer, nullable=False)
    no_ca_5 = sa.Column("NO_CA_5", sa.Integer, nullable=False)
    no_ca_6 = sa.Column("NO_CA_6", sa.Integer, nullable=False)

    ac_logical_no = sa.Column("AC_LOGICAL_NO", sa.Integer, nullable=False)
    registration = sa.Column("REGISTRATION", sa.String(10), nullable=False)

    leg_no = sa.Column("LEG_NO", sa.Integer, nullable=False)
    leg_type = sa.Column("LEG_TYPE", sa.String(1), nullable=False)

    employer_cockpit = sa.Column("EMPLOYER_COCKPIT", sa.String(3), nullable=False)
    employer_cabin = sa.Column("EMPLOYER_CABIN", sa.String(3), nullable=False)
    add_crew_employer = sa.Column("ADD_CREW_EMPLOYER", sa.String(3), nullable=False)

    no_of_seats = sa.Column("NO_OF_SEATS", sa.Integer, nullable=False)
    duty_time = sa.Column("DUTY_TIME", sa.Integer, nullable=False)

    unique_counter = sa.Column("UNIQUE_COUNTER", sa.Integer, nullable=False)

    cat = sa.Column("CAT", sa.String(4), nullable=False)
    markers = sa.Column("MARKERS", sa.Integer, nullable=False)

    modification_value = sa.Column("MODIFICATION_VALUE", sa.Integer, nullable=False)
    external_id = sa.Column("EXTERNAL_ID", sa.Integer, nullable=False)

    source_of_leg = sa.Column("SOURCE_OF_LEG", sa.String(1), nullable=False)
    time_stamp = sa.Column("TIME_STAMP", sa.Integer, nullable=False)

    leg_state = sa.Column("LEG_STATE", sa.String(3), nullable=False)
    scd_arr_ap = sa.Column("SCD_ARR_AP", sa.String(3), nullable=False)

    ac_owner = sa.Column("AC_OWNER", sa.String(3), nullable=False)
    location_code = sa.Column("LOCATION_CODE", sa.String(9), nullable=False)

    pred_uno = sa.Column("PRED_UNO", sa.Integer, nullable=False)
    succ_uno = sa.Column("SUCC_UNO", sa.Integer, nullable=False)

    pred_connect_time = sa.Column("PRED_CONNECT_TIME", sa.Integer, nullable=False)
    succ_connect_time = sa.Column("SUCC_CONNECT_TIME", sa.Integer, nullable=False)

    pred_ct_type = sa.Column("PRED_CT_TYPE", sa.String(1), nullable=False)
    succ_ct_type = sa.Column("SUCC_CT_TYPE", sa.String(1), nullable=False)

    no_seats_fd_cl_1 = sa.Column("NO_SEATS_FD_CL_1", sa.Integer, nullable=False)
    no_seats_fd_cl_2 = sa.Column("NO_SEATS_FD_CL_2", sa.Integer, nullable=False)
    no_seats_fd_cl_3 = sa.Column("NO_SEATS_FD_CL_3", sa.Integer, nullable=False)

    no_seats_cab_cl_1 = sa.Column("NO_SEATS_CAB_CL_1", sa.Integer, nullable=False)
    no_seats_cab_cl_2 = sa.Column("NO_SEATS_CAB_CL_2", sa.Integer, nullable=False)
    no_seats_cab_cl_3 = sa.Column("NO_SEATS_CAB_CL_3", sa.Integer, nullable=False)

    @hybrid_property
    def is_leg(self):
        return self.type_ == 'L'

    @hybrid_property
    def is_deadhead(self):
        return self.type_ == 'F'


class NonCrewMember(TrimmedNameMixin, LSYBase):
    __tablename__ = "NON_CREW_MEMBER"

    employee_id = sa.Column(sa.String(12), primary_key=True, nullable=False)

    first_name = sa.Column(sa.String(30), nullable=False)
    middle_name = sa.Column(sa.String(30), nullable=False)
    name = sa.Column(sa.String(30), nullable=False)

    birth_date = sa.Column(sa.Date, nullable=False)

    place_of_birth = sa.Column(sa.String(25), nullable=False)
    state_of_birth = sa.Column(sa.String(25), nullable=False)
    country_of_birth = sa.Column(sa.String(40), nullable=False)

    sex = sa.Column(sa.String(1), nullable=False)
    status_on_board = sa.Column(sa.String(2), nullable=False)
    nationality = sa.Column(sa.String(3), nullable=False)

    remark = sa.Column(sa.String(254), nullable=False)

    @hybrid_property
    def employee_no(self):
        # compatibility name with CrewMember
        return self.employee_id

    @employee_no.expression
    def employee_no(cls):
        return cls.employee_id


class RemarkOfEvent(LSYBase):
    __tablename__ = "REMARK_OF_EVENT"

    __remark_separator__ = '|'

    __value_separator__ = ';'

    uno = sa.Column("UNO", sa.Integer, primary_key=True, nullable=False)
    type_ = sa.Column("TYPE", sa.String(1), primary_key=True, nullable=False)

    remark = sa.Column("REMARK", sa.String(254), nullable=False)
    event_type = sa.Column("EVENT_TYPE", sa.String(1), nullable=False)

    day_of_origin = sa.Column("DAY_OF_ORIGIN", sa.Date, nullable=False)

    airline = sa.Column("AIRLINE", sa.String(3), nullable=False)
    flight_no = sa.Column("FLIGHT_NO", sa.Integer, nullable=False)
    suffix = sa.Column("SUFFIX", sa.String(1), nullable=False)

    dep_ap = sa.Column("DEP_AP", sa.String(3), nullable=False)
    counter = sa.Column("COUNTER", sa.Integer, nullable=False)

    code = sa.Column("CODE", sa.String(9), nullable=False)
    arr_ap = sa.Column("ARR_AP", sa.String(3), nullable=False)

    begin_date = sa.Column("BEGIN_DATE", sa.Date, nullable=False)
    begin_time = sa.Column("BEGIN_TIME", sa.String(4), nullable=False)

    ac_type_code = sa.Column("AC_TYPE_CODE", sa.String(4), nullable=False)

    @hybrid_property
    def is_jumpseat(self):
        return self.type_ == 'J'

    def parse_jumpseat_substrings(self):
        """
        Slit remark string for possible jumpseats hiding in there. Each
        substring may be a special string requiring looking up the person from
        another table; or their another string separated by a delimiter of
        thier name, employee, and seat information.
        """
        for remark_substr in self.remark.split(self.__remark_separator__):
            person_type = remark_substr[0]
            remaining = remark_substr[1:]
            yield (person_type, remaining)

    def split_remark_for_jumpseats(self, session):
        """
        Yield fully structured person dicts for all jumpseat remarks.
        """
        for person_type, remaining in self.parse_jumpseat_substrings():
            query = JumpseatQueryManager.build_query(person_type, remaining)
            if query is not None:
                # known person type, fetch from DB
                for row in session.execute(query).mappings():
                    yield dict(row)
            else:
                # unknown / Other jumpseat type, parse inline
                person = dict(
                    zip(
                        ['last_name', 'first_name', 'employee_number', 'seat', 'seat_order'],
                        remaining.split(self.__value_separator__),
                        strict=True
                    )
                )
                person['seat'] = 'ACM'
                person['seat_order'] = 999
                person['source'] = f'parse with {self.__value_separator__}'
                yield person


class JumpseatQueryManager:
    """
    Builds queries for known person types (CrewMember, NonCrewMember).
    """
    
    models = {
        'C': (CrewMember, CrewMember.employee_no),
        'N': (NonCrewMember, NonCrewMember.employee_id),
    }

    @classmethod
    def build_query(cls, person_type: str, person_id: str):
        """Return a SQLAlchemy selectable or None if unknown type."""
        if person_type not in cls.models:
            return None

        model, id_field = cls.models[person_type]
        return sa.select(
            model.trimmed_first_name().label('last_name'),
            model.trimmed_name().label('first_name'),
            model.trimmed_employee_no().label('employee_number'),
            sa.literal('ACM').label('seat'),
            sa.literal(999).label('seat_order'),
            sa.literal(f'{model.__name__} lookup').label('source'),
        ).where(id_field == person_id)
