# Constants
from enum import Enum
from typing import Tuple
from .timepoint import TimePoint
from .timeelement import TimeElement

from .units_constants import START_YEAR, END_YEAR


START_DATE_ELEMENTS_GRE: Tuple[TimeElement, ...] = (
    TimeElement("YR", START_YEAR),
    TimeElement("MH", 1),
    TimeElement("DY", 1),
    TimeElement("HR", 0),
    TimeElement("ME", 0),
    TimeElement("SD", 0),
)

END_DATE_ELEMENTS_GRE: Tuple[TimeElement, ...] = (
    TimeElement("YR", END_YEAR),
    TimeElement("MH", 1),
    TimeElement("DY", 1),
    TimeElement("HR", 0),
    TimeElement("ME", 0),
    TimeElement("SD", 0),
)

START_DATE_ELEMENTS_ISO: Tuple[TimeElement, ...] = (
    TimeElement("YR", START_YEAR),
    TimeElement("WK", 1),
    TimeElement("WY", 3),
    TimeElement("HR", 0),
    TimeElement("ME", 0),
    TimeElement("SD", 0),
)

END_DATE_ELEMENTS_ISO: Tuple[TimeElement, ...] = (
    TimeElement("YR", END_YEAR),
    TimeElement("WK", 1),
    TimeElement("WY", 3),
    TimeElement("HR", 0),
    TimeElement("ME", 0),
    TimeElement("SD", 0),
)

START_POINT_GRE = TimePoint(
    [
        TimeElement("YR", START_YEAR),
        TimeElement("MH", 1),
        TimeElement("DY", 1),
        TimeElement("HR", 0),
        TimeElement("ME", 0),
        TimeElement("SD", 0),
    ]
)
""" start date  of the time range as Timepoint object in Gregorian calendar

        Note: do not import it in timepoint.py and timeelement.py"""

END_POINT_GRE = TimePoint(
    [
        TimeElement("YR", END_YEAR),
        TimeElement("MH", 12),
        TimeElement("DY", 31),
        TimeElement("HR", 23),
        TimeElement("ME", 59),
        TimeElement("SD", 59),
    ]
)
""" end date of the time range as Timepoint object in Gregorian calendar

        Note: do not import it in timepoint.py and timeelement.py"""

START_POINT_ISO = TimePoint(
    [
        TimeElement("YR", START_YEAR),
        TimeElement("WK", 1),
        TimeElement("WY", 3),
        TimeElement("HR", 0),
        TimeElement("ME", 0),
        TimeElement("SD", 0),
    ]
)
""" start date of time range as Timepoint object in ISO calendar"

    Note: do not import it in timepoint.py and timeelement.py"""

END_POINT_ISO = TimePoint(
    [
        TimeElement("YR", END_YEAR),
        TimeElement("WK", 1),
        TimeElement("WY", 3),
        TimeElement("HR", 0),
        TimeElement("ME", 0),
        TimeElement("SD", 0),
    ]
)
""" end date of time range as Timepoint object in ISO calendar

        Note: do not import it in timepoint.py and timeelement.py"""


class SpanContain(Enum):
    AHEAD = "ahead"
    INSIDE = "inside"
    BEHIND = "behind"
    END_OVERLAPPED = "end_overlapped"
    START_OVERLAPPED = "start_overlapped"
    ERROR = "error"


class SequnceName(Enum):
    GRE = "gre"
    ISO = "iso"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class PeriodType(Enum):
    START_START = "start_start"
    START_END = "end_end"
    END_START = "end_start"
    END_END = "end_end"
    BEFORE = "before"
    AFTER = "after"
    SINGLE_POINT = "single_point"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class SpanType(Enum):
    BETWEEN = "between"
    BEFORE = "before"
    AFTER = "after"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class EdgeType(Enum):
    START = "start"
    END = "end"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
