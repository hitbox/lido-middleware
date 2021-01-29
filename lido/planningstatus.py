from enum import Enum

class PlanningStatus(Enum):
    """
    TODO: document this.
    """

    def __init__(self, code, description):
        self.code = code
        self.description = description

    TIME_DRIVEN_MODE = (
        1, 'time driven mode (approx. at STD – 5 hrs, AOS is not triggered)')
    FIRST_ESTIMATES_WAB = (
        2, 'first estimates WAB (approx. at STD – 3,5 hrs)')
    FINAL_ESTIMATES_WAB = (
        3, 'final estimates WAB (approx. at STD – 1 hr, AOS is not triggered)')
    LOAD_SHEET_INFORMATION = (
        4, 'load sheet information (actual values for ZFW and fuel, shortly'
           ' before off-block, AOS is not triggered)')
    LOAD_INFORMATION_FROM_WB_AGENT = (
        5, 'Load information from W&B agent (no DOW, at any time)')
    #
    LOAD_INFORMATION_FROM_WB_AGENT_NO_AUTO1 = (
        51, 'like LOAD_INFORMATION_FROM_WB_AGENT, but no automatic calculation in AOS')
    LOAD_INFORMATION_FROM_WB_AGENT_NO_AUTO2 = (
        52, 'like LOAD_INFORMATION_FROM_WB_AGENT, but no automatic calculation in AOS')
    LOAD_INFORMATION_FROM_WB_AGENT_NO_AUTO3 = (
        53, 'like LOAD_INFORMATION_FROM_WB_AGENT, but no automatic calculation in AOS')
    LOAD_INFORMATION_FROM_WB_AGENT_NO_AUTO4 = (
        54, 'like LOAD_INFORMATION_FROM_WB_AGENT, but no automatic calculation in AOS')
    LOAD_INFORMATION_FROM_WB_AGENT_NO_AUTO5 = (
        55, 'like LOAD_INFORMATION_FROM_WB_AGENT, but no automatic calculation in AOS')
    # was referenced in the documentation, so it is included just for the code number
    UNKNOWN = (95, 'unknown')


# formatting string for weight and balance fields that depend on planning status.

# Dry Operating Weight format string from PlanningStatus
# NOTE: interf_IN_Weight_and_Balance_Data_583_v1_0.pdf
#       Page 7
#       In case of planning status 01, 02, 03: 042650
#       In case of planning status 04 or 95: BLANK
DRY_OPERATING_WEIGHT_PLANNINGSTATUS_FORMAT = {
    PlanningStatus.LOAD_SHEET_INFORMATION: ' ' * 6,
    PlanningStatus.UNKNOWN: ' ' * 6,
}

for key in [
        PlanningStatus.TIME_DRIVEN_MODE,
        PlanningStatus.FIRST_ESTIMATES_WAB,
        PlanningStatus.FINAL_ESTIMATES_WAB,
]:
    DRY_OPERATING_WEIGHT_PLANNINGSTATUS_FORMAT[key] = '{dry_operating_index:0>6}'

# Estimated Total Traffic Load format string from PlanningStatus
# NOTE: interf_IN_Weight_and_Balance_Data_583_v1_0.pdf
#       Page 7
#       In case of planning status 01, 02, 03, 05: e.g. 007000, 012345, ...
#       In case of planning status 04: 000000
ESTIMATED_TOTAL_TRAFFIC_LOAD_FORMAT = {
    PlanningStatus.LOAD_SHEET_INFORMATION: '0' * 6,
}
for key in [
        PlanningStatus.TIME_DRIVEN_MODE,
        PlanningStatus.FIRST_ESTIMATES_WAB,
        PlanningStatus.FINAL_ESTIMATES_WAB,
        PlanningStatus.LOAD_INFORMATION_FROM_WB_AGENT,
]:
    ESTIMATED_TOTAL_TRAFFIC_LOAD_FORMAT[key] = '{estimated_total_traffic_load:0>6}'

# Actual Zero Fuel Weight (ZFW) and Takeoff fuel same formatting plan.
# NOTE: interf_IN_Weight_and_Balance_Data_583_v1_0.pdf
#       Page 7
#       In case of planning status 04: e.g. 052000 or 001234
#       In case of planning status 01, 02, 03 or 05: 000000
ACTUAL_ZERO_FUEL_WEIGHT_FORMAT = {
    PlanningStatus.LOAD_SHEET_INFORMATION: '{actual_zero_fuel_weight:0>6}'
}
ACTUAL_TAKEOFF_FUEL_FORMAT = {
    PlanningStatus.LOAD_SHEET_INFORMATION: '{actual_takeoff_fuel:0>6}'
}
for key in [
        PlanningStatus.TIME_DRIVEN_MODE,
        PlanningStatus.FIRST_ESTIMATES_WAB,
        PlanningStatus.FINAL_ESTIMATES_WAB,
        PlanningStatus.LOAD_INFORMATION_FROM_WB_AGENT,
]:
    ACTUAL_ZERO_FUEL_WEIGHT_FORMAT[key] = '0' * 6
    ACTUAL_TAKEOFF_FUEL_FORMAT[key] = '0' * 6

del key
