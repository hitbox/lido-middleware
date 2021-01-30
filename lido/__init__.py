import inspect

from datetime import date

DATEFMT = '%d%b%Y'
TIMEFMT = '%H%M%S'

AIRLINE_DESIGNATOR = {
    'ABX': 'GB',
    'ATI': '8C',
}

class LIDOError(Exception):
    """
    """


class LIDOWeightBalanceMessage:
    """
    Renders LIDO weight and balance message from LoadPlan object.
    """

    MESSAGE_FORMAT_STRING = (
        'WAB'
        '{timestamp_in_gmt}'
        '{airline_designator}'
        '{flight_number}'
        '{operational_suffix}'
        '{date_of_origin}'
        '{departure_airport_iata}'
        '{destination_airport_iata}'
        '{planning_status}'
        '{duplicate_number}'
        '{revision_number}'
        '{dry_operating_weight}'
        '{estimated_total_traffic_load}'
        '{pax_baggage_indicator}'
        '{cargo_mail_indicator}'
        '{transit_load_indicator}'
        '{tail_tank_indicator}'
        '{center_of_gravity}'
        '{actual_zero_fuel_weight}'
        '{actual_takeoff_fuel}'
        '{estimated_pax}'
        '{unit_of_measure}'
        '{dry_operating_index}'
        '{cargo_weight}'
        '{separator}'
        '{estimated_pax_class_one}'
        '{estimated_pax_class_two}'
        '{estimated_pax_class_three}'
    )

    # something is wrong if the final message is not this length:
    MESSAGELENGTH = 130

    def __init__(self, loadplan, icao2iata):
        self.loadplan = loadplan
        self.icao2iata = icao2iata

    def get_context(self):
        """
        Return dict context for format string.
        """
        context = {name: getattr(self, name) for name in dir(self)
                   if name.islower() and not name.startswith('_')}
        context = {key: attr for key, attr in context.items()
                   if not inspect.ismethod(attr)}
        return context

    def __str__(self):
        context = self.get_context()
        msg = self.MESSAGE_FORMAT_STRING.format(**context)
        if len(msg) != self.MESSAGELENGTH:
            raise LIDOError('LIDO message invalid length, %r' % len(msg))
        return msg

    @property
    def timestamp_in_gmt(self):
        """
        WABFORMAT.txt:2
        """
        value = self.loadplan.print_time_gmt
        return value.strftime(DATEFMT + TIMEFMT).upper()

    @property
    def airline_designator(self):
        """
        WABFORMAT.txt:3
        """
        company = self.loadplan.company
        designator = AIRLINE_DESIGNATOR[company]
        return '{: <3}'.format(designator)

    @property
    def flight_number(self):
        """
        WABFORMAT.txt:4
        """
        return '{: >5}'.format(self.loadplan.flight_number)

    @property
    def operational_suffix(self):
        """
        WABFORMAT.txt:5
        A-Z or BLANK
        """
        return'{: >1}'.format(' ')

    @property
    def date_of_origin(self):
        """
        WABFORMAT.txt:6
        """
        date_of_origin = self.loadplan.print_time_gmt.date()
        date_of_orign = date(date_of_origin.year, date_of_origin.month, self.loadplan.day)
        return date_of_origin.strftime(DATEFMT).upper()

    @property
    def departure_airport_iata(self):
        """
        WABFORMAT.txt:7
        """
        station = self.loadplan.origin_station
        station = self.icao2iata[station]
        return '{: <5}'.format(station)

    @property
    def destination_airport_iata(self):
        """
        WABFORMAT.txt:8
        """
        station = self.loadplan.destination_station
        station = self.icao2iata[station]
        return '{: <5}'.format(station)

    @property
    def planning_status(self):
        """
        WABFORMAT.txt:9
        """
        return '04'

    @property
    def duplicate_number(self):
        """
        WABFORMAT.txt:10
        Default 1.
        """
        return '1'

    @property
    def revision_number(self):
        """
        WABFORMAT.txt:11
        Default 00.
        """
        return '00'

    @property
    def dry_operating_weight(self):
        """
        WABFORMAT.txt:12
        Dry Operating Weight (DOW)
        depends on planning status.
        """
        if self.planning_status in ('04', '95'):
            return ' ' * 6
        else:
            for weight in self.loadplan.weights:
                if weight.name == 'OEW':
                    value = weight.weight
                    return '{:0>6}'.format(value)
            raise LIDOError('Unable to find dry operating weight.')

    @property
    def estimated_total_traffic_load(self):
        """
        WABFORMAT.txt:13
        Est. Total Traffic Load
        depends on planning status.
        """
        if self.planning_status in ('04', ):
            return '0' * 6
        else:
            raise NotImplementedError

    @property
    def pax_baggage_indicator(self):
        """
        WABFORMAT.txt:14
        Y/N
        """
        return 'N'

    @property
    def cargo_mail_indicator(self):
        """
        WABFORMAT.txt:15
        Y/N
        """
        return 'N'

    @property
    def transit_load_indicator(self):
        """
        WABFORMAT.txt:16
        Y/N
        """
        return 'N'

    @property
    def tail_tank_indicator(self):
        """
        WABFORMAT.txt:17
        Y/N/BLANK
        """
        return ' '

    @property
    def center_of_gravity(self):
        """
        WABFORMAT.txt:18
        00000; 09.23; 15.12
        """
        for weight in self.loadplan.weights:
            if weight.name == 'OEW':
                value = float(weight.cg_percent_mac)
                return '{:0>5.2f}'.format(value)
        raise LIDOError('Unable to find OEW center of gravity.')

    @property
    def actual_zero_fuel_weight(self):
        """
        WABFORMAT.txt:19
        depends on planning status.
        """
        for weight in self.loadplan.weights:
            if weight.name == 'Zero Fuel':
                value = weight.weight
                return '{:0>6}'.format(value)
        raise LIDOError('Unable to find zero fuel weight.')

    @property
    def actual_takeoff_fuel(self):
        """
        WABFORMAT.txt:20
        actual_takeoff_fuel
        depends on planning status.
        """
        for weight in self.loadplan.weights:
            if weight.name == 'Takeoff':
                value = weight.weight
                return '{:0>6}'.format(value)
        raise LIDOError('Unable to find takeoff fuel weight.')

    @property
    def estimated_pax(self):
        """
        WABFORMAT.txt:21
        Number of estim. PAX [sic]
        """
        return '{:0>4}'.format('0')

    @property
    def unit_of_measure(self):
        """
        WABFORMAT.txt:22
        K/L. BLANK is K.
        """
        return self.loadplan.all_weights_unit[:1]

    @property
    def dry_operating_index(self):
        """
        WABFORMAT.txt:23
        {:0<5} if available else BLANK*5.
        """
        return '{:0>5}'.format('     ')

    @property
    def cargo_weight(self):
        """
        WABFORMAT.txt:24
        {:0<6} if available else BLANK*6.
        """
        for acconfig in self.loadplan.aircraft_configurations:
            if acconfig.name == 'Cargo Wt':
                value = int(acconfig.value)
                return '{:0>6}'.format(value)
        raise LIDOError('Unable to find cargo weight.')

    @property
    def separator(self):
        """
        WABFORMAT.txt:25
        separator
        Space for further extensions.
        """
        return ' ' * 18

    @property
    def estimated_pax_class_one(self):
        """
        WABFORMAT.txt:26
        {:0<4} if available else BLANK*4 -#}
        """
        return '{:0>4}'.format('    ')

    @property
    def estimated_pax_class_two(self):
        """
        WABFORMAT.txt:27
        {:0<4} if available else BLANK*4 -#}
        """
        return '{:0>4}'.format('    ')

    @property
    def estimated_pax_class_three(self):
        """
        WABFORMAT.txt:28
        {:0<4} if available else BLANK*4 -#}
        """
        return '{:0>4}'.format('    ')
