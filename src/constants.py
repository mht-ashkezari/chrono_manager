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
    AHEAD = "SpanContain.AHEAD"
    INSIDE = "SpanContain.INSIDE"
    BEHIND = "SpanContain.BEHIND"
    END_OVERLAPPED = "SpanContain.END_OVERLAPPED"
    START_OVERLAPPED = "SpanContain.START_OVERLAPPED"
    ERROR = "SpanContain.ERROR"


class SequnceName(Enum):
    GRE = "gre"
    ISO = "iso"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class PeriodType(Enum):
    START_START = "PeriodType.START_START"
    START_END = "PeriodType.START_END"
    END_START = "PeriodType.END_START"
    END_END = "PeriodType.END_END"
    BEFORE = "PeriodType.BEFORE"
    AFTER = "PeriodType.AFTER"
    SINGLE_POINT = "PeriodType.SINGLE_POINT"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class SpanType(Enum):
    BETWEEN = "SpanType.BETWEEN"
    BEFORE = "SpanType.BEFORE"
    AFTER = "SpanType.AFTER"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class EdgeType(Enum):
    START = "EdgeType.START"
    END = "EdgeType.END"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
