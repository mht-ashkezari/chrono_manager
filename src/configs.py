from typing import Tuple
from .timeelement import TimeElement
from .units_constants import START_YEAR, END_YEAR
from datetime import date
from enum import Enum


END_SCOPE_ELEMENTS_GRE: Tuple[TimeElement, ...] = (
    TimeElement("YR", END_YEAR),
    TimeElement("MH", 12),
    TimeElement("DY", 31),
    TimeElement("HR", 23),
    TimeElement("ME", 59),
    TimeElement("SD", 59),
)
END_SCOPE_ELEMENTS_ISO: Tuple[TimeElement, ...] = (
    TimeElement("YR", END_YEAR),
    TimeElement("WK", 53),
    TimeElement("WY", 7),
    TimeElement("HR", 23),
    TimeElement("ME", 59),
    TimeElement("SD", 59),
)
START_SCOPE_ELEMENTS_GRE: Tuple[TimeElement, ...] = (
    TimeElement("YR", START_YEAR),
    TimeElement("MH", 1),
    TimeElement("DY", 1),
    TimeElement("HR", 0),
    TimeElement("ME", 0),
    TimeElement("SD", 0),
)
START_SCOPE_ELEMENTS_ISO: Tuple[TimeElement, ...] = (
    TimeElement("YR", START_YEAR),
    TimeElement("WK", 1),
    TimeElement("WY", 1),
    TimeElement("HR", 0),
    TimeElement("ME", 0),
    TimeElement("SD", 0),
)


def years_with_53_weeks(start_year: int, end_year: int) -> frozenset[int]:
    years = set()
    for year in range(start_year, end_year + 1):
        d = date(year, 12, 28)
        if d.isocalendar()[1] == 53:
            years.add(year)
    return frozenset(years)


YEARS_WITH_53_WEEKS: frozenset[int] = years_with_53_weeks(START_YEAR, END_YEAR)


class PointType(Enum):
    START = "start"
    END = "end"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class CompareSequnce(Enum):
    GRE = "iso"
    ISO = "gre"
    ISO_GRE = "iso_gre"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
