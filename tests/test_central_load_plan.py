import datetime
import json
import unittest

import central_load_plan.email
import central_load_plan.crewmember

# hand crafted for both companies
TESTDATA = dict(
    leg_departure_date_utc = datetime.datetime(2021,3,5,6,12),
    flight_plan_id = 3,
    flight_number = 1234,
    origin_iata = 'OOO',
    destination_iata = 'DDD',
    aircraft_registration = 'TAIL',
    estimated_block_time = datetime.time(6,13),
    scheduled_departure_time = datetime.time(6,14),
    estimated_time_enroute = datetime.time(1,3),
    estimated_arrival_time = datetime.time(2,4),
    planned_payload = 11_111,
    ramp_fuel = 22_222,
    fuel_burn = 3_333,
    taxi_fuel = 444,
    ballast_fuel = 555,
    max_payload = 20_000,
    mzfw = 19_999,
    mtow = 30_000,
    mldg = 29_999,
    crewmembers = [
        dict(seat='PIC', first_name='F1', last_name='L1', employee_number='EE1'),
        dict(seat='SIC', first_name='F2', last_name='L2', employee_number='EE2'),
        dict(seat='SIC', first_name='F3', last_name='L3', employee_number='EE3'),
        dict(seat='IRO', first_name='F4', last_name='L4', employee_number='EE4'),
        dict(seat='CP', first_name='F5', last_name='L5', employee_number='EE5'),
        dict(seat='FA', first_name='F6', last_name='L6', employee_number='EE6'),
        dict(seat='J', first_name='F7', last_name='L7', employee_number='EE7'),
        dict(seat='J', first_name='F8', last_name='L8', employee_number='EE8'),
        dict(seat='J', first_name='F9', last_name='L9', employee_number='EE9'),
    ],
    aircraft_equipment_status = [
        dict(
            item = 'ABC-123-456',
            description = ('DEF ABC-123-456  Some text with sometimes'
                '  weird runs of whitespace.  And some text on the end we'
                ' want put on a newline: Some filler text.   Expiration'
                ' Date: 2021-11-13')
        ),
        dict(
            item = 'GHI 123',
            description = 'GHI 123 A very short one. Expiration Date: 2021-11-13'
        ),
        dict(
            item = '12-34-56-78',
            description = 'ATI-12-34-56-78 Aft cargo door stop fwd frame 4th from top missing    Expiration Date: 11/23/2021 11:59:59 PM',
        ),
    ]
)

ATI_WANTS = '''\


LEG DEPARTURE DATE (UTC): 05MAR21 (0612Z) VER NO: 3
FLT #  ORIG  DEST  TAIL #  STE   STD      ETE    PLANNED BLOCK TIME
1234   OOO   DDD   TAIL    06:13 01/0614  01:03  06:13

*** ALL PAYLOAD AND FUEL DATA BELOW IN {LBS} ***
*** BALLAST FUEL IS INCLUDED IN THE  RAMP FUEL VALUE ***

PLND PAYLOAD    RAMP FUEL   FUEL BURN   TAXI FUEL   UNUSABLE FUEL
11111           22222       3333        444         555         

MAX PAYLOAD   MZFW      MTOW       MLDG      OEW/BOW
20000         19999     30000      29999     

SEAT    FIRST NAME      LAST NAME       EMPLOYEE #
----    ----------      ---------       ----------
PIC     F1              L1              EE1         
SIC     F2              L2              EE2         
SIC     F3              L3              EE3         
IRO     F4              L4              EE4         
CP      F5              L5              EE5         
FA      F6              L6              EE6         
J       F7              L7              EE7         
J       F8              L8              EE8         
J       F9              L9              EE9         

--- A/C EQUIPMENT STATUS ---
ITEM          DESCRIPTION
ABC-123-456   Some text with sometimes  weird runs of whitespace.  And some text
              on the end we want put on a newline: Some filler
              text.
              Expiration Date: 2021-11-13

GHI 123       GHI 123 A very short one.
              Expiration Date: 2021-11-13

12-34-56-78   Aft cargo door stop fwd frame 4th from top missing
              Expiration Date: 11/23/2021 11:59:59 PM


*** OFP IS THE CONTROLLING DOCUMENT FOR DATA PRODUCED FOR THIS MESSAGE. ***'''

ABX_WANTS = '''\


LEG DEPARTURE DATE (UTC): 05MAR21 (0612Z) VER NO: 3
FLT #  ORIG  DEST  TAIL #  STE   STD      ETD    ETA
1234   OOO   DDD   TAIL    06:13 01/0614  02:04  01/0204

*** ALL PAYLOAD AND FUEL DATA BELOW IN {LBS} ***
*** BALLAST FUEL IS INCLUDED IN THE  RAMP FUEL VALUE ***

PLND PAYLOAD    RAMP FUEL   FUEL BURN   TAXI FUEL   BALLAST FUEL
11111           22222       3333        444         555         

MAX PAYLOAD     MZFW        MTOW        MLDG
20000           19999       30000       29999     

SEAT    FIRST NAME      LAST NAME       EMPLOYEE #
----    ----------      ---------       ----------
PIC     F1              L1              EE1         
SIC     F2              L2              EE2         
SIC     F3              L3              EE3         
IRO     F4              L4              EE4         
CP      F5              L5              EE5         
FA      F6              L6              EE6         
J       F7              L7              EE7         
J       F8              L8              EE8         
J       F9              L9              EE9         

--- A/C EQUIPMENT STATUS ---
ITEM          DESCRIPTION
ABC-123-456   DEF ABC-123-456  Some text with sometimes  weird runs of
              whitespace.  And some text on the end we want put on
              a newline: Some filler text.   Expiration Date:
              2021-11-13
GHI 123       GHI 123 A very short one. Expiration Date: 2021-11-13
12-34-56-78   ATI-12-34-56-78 Aft cargo door stop fwd frame 4th from top missing
              Expiration Date: 11/23/2021 11:59:59 PM


*** OFP IS THE CONTROLLING DOCUMENT FOR DATA PRODUCED FOR THIS MESSAGE. ***'''

class TestCentralLoadPlanEmail(unittest.TestCase):

    def setUp(self):
        self.render = central_load_plan.email.render

    def test_render_template_ati(self):
        template = 'central_load_plan/templates/email_8C.txt'
        emailconf = dict(template=template)
        result = self.render(emailconf, TESTDATA)
        self.assertEqual(result, ATI_WANTS)

    @unittest.skip('Things have changed and not sure how to test now.')
    def test_render_template_abx(self):
        template = 'central_load_plan/templates/email_GB.txt'
        emailconf = dict(template=template)
        result = self.render(emailconf, TESTDATA)
        self.assertEqual(result, ABX_WANTS)


class TestCentralLoadPlanCrewmembers(unittest.TestCase):
    """
    Test parsing jump seats and crew members.
    """

    def setUp(self):
        self.jumpseat_type_and_remaining = central_load_plan.crewmember.jumpseat_type_and_remaining
        self.parse_for_other = central_load_plan.crewmember.parse_for_other

    def test_parse_remark(self):
        """
        Test parsing remark field for jump seaters.
        """
        remark_tests = [
            (
                # no other types
                "C12345|C65789",
                tuple(),
            ),
            (
                # only other type
                "OLAST;FIRST;123456;YV;3",
                (
                    dict(
                        last_name="LAST",
                        first_name="FIRST",
                        employee_number="123456",
                        seat="YV",
                        seat_order="3"
                    ),
                ),
            ),
            (
                # mixed types
                "C12345|C65789|OLAST;FIRST;1234;WQ;3",
                (
                    dict(
                        last_name="LAST",
                        first_name="FIRST",
                        employee_number="1234",
                        seat="WQ",
                        seat_order="3",
                    ),
                ),
            ),
        ]
        for source, expect in remark_tests:
            crewmembers = []
            for substring in source.split('|'):
                type_, remaining = self.jumpseat_type_and_remaining(substring)
                if type_ == 'O':
                    person_dict = self.parse_for_other(remaining)
                    crewmembers.append(person_dict)
            self.assertEqual(tuple(crewmembers), expect)

if __name__ == '__main__':
    unittest.main()
