from typing import Callable, Dict, List, Tuple, Union, cast
from frozendict import frozendict
import datetime

START_YEAR = 1800
END_YEAR = 2199

UNITS_SEQUENCE: Dict[str, Tuple[str, ...]] = {
    "gre": ("YR", "MH", "DY", "HR", "ME", "SD"),
    "iso": ("YR", "WK", "WY", "HR", "ME", "SD"),
}

START_SCOPE_VALUES_GRE: Tuple[int, ...] = (START_YEAR, 1, 1, 0, 0, 0)
END_SCOPE_VALUES_GRE: Tuple[int, ...] = (END_YEAR, 12, 31, 23, 59, 59)
START_SCOPE_VALUES_ISO: Tuple[int, ...] = (START_YEAR, 1, 1, 0, 0, 0)
END_SCOPE_VALUES_ISO: Tuple[int, ...] = (END_YEAR, 53, 7, 23, 59, 59)

time_spans_types = ["between", "outside", "before", "after"]
time_span_len_type = ["begin", "end"]
weekdays_names = {
    i + 1: val
    for i, val in enumerate(
        [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
    )
}

START_DATE = datetime.datetime(START_YEAR, 1, 1, 0, 0, 0)
END_DATE = datetime.datetime(END_YEAR + 1, 1, 1, 0, 0, 0)


START_DATE_VLAUES_GRE: Tuple[int, ...] = (START_YEAR, 1, 1, 0, 0, 0)
END_DATE_VLAUES_GRE: Tuple[int, ...] = (END_YEAR + 1, 1, 1, 0, 0, 0)
START_DATE_VLAUES_ISO: Tuple[int, ...] = (START_YEAR, 1, 3, 0, 0, 0)
END_DATE_VLAUES_ISO: Tuple[int, ...] = (END_YEAR + 1, 1, 3, 0, 0, 0)


month_allowed_values = frozendict(
    {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }
)

day_allow_vals = frozendict(
    {
        "Jan": {"min": 1, "max": 31},
        "Feb": {"min": 1, "max": 29},
        "Mar": {"min": 1, "max": 31},
        "Apr": {"min": 1, "max": 30},
        "May": {"min": 1, "max": 31},
        "Jun": {"min": 1, "max": 30},
        "Jul": {"min": 1, "max": 31},
        "Aug": {"min": 1, "max": 31},
        "Sep": {"min": 1, "max": 30},
        "Oct": {"min": 1, "max": 31},
        "Nov": {"min": 1, "max": 30},
        "Dec": {"min": 1, "max": 31},
    }
)


TimeUnitInfo = Dict[
    str,
    Union[
        str,
        int,
        Dict[str, int],
        Dict[str, Dict[str, int]],
        Callable[[int], List[int]],
        Callable[[int, Union[int, None]], List[int]],
        Callable[[int], str],
        List[str],
        float,
        Callable[[str, bool], int],
        Callable[[bool], int],
    ],
]


UNITS: Dict[str, TimeUnitInfo] = {
    "SD": {
        "unit_name": "second",
        "value_type": "range",
        "allowed_values": {"min": 0, "max": 59},
        "default_pattern": r"(:[0-5]\d\.)",
        "alternative_pattern": r"(S[0-5]\d)",
        "default_representation": lambda value: f":{value:02d}.",
        "alternative_representation": lambda value: f"S{value:02d}",
        "over_join_units": ["ME"],
        "under_join_units": [],
        "unit_as_seconds": 1,
        " values_to_end_scope": lambda start_value: list(range(start_value, 60)),
    },
    "ME": {
        "unit_name": "minute",
        "value_type": "range",
        "allowed_values": {"min": 0, "max": 59},
        "default_pattern": r"(:[0-5]\d)",
        "alternative_pattern": r"(M[0-5]\d)",
        "default_representation": lambda value: f":{value:02d}",
        "alternative_representation": lambda value: f"M{value:02d}",
        "over_join_units": ["HR"],
        "under_join_units": ["SD"],
        "unit_as_seconds": 60,
        " values_to_end_scope": lambda start_value: list(range(start_value, 60)),
    },
    "HR": {
        "unit_name": "hour",
        "value_type": "range",
        "allowed_values": {"min": 0, "max": 23},
        "default_pattern": r"(T[01]\d|T2[0-3])",
        "alternative_pattern": r"(H[01]\d|H2[0-3])",
        "default_representation": lambda value: f"T{value:02d}",
        "alternative_representation": lambda value: f"H{value:02d}",
        "over_join_units": ["DY", "WY"],
        "under_join_units": ["ME"],
        "unit_as_seconds": 3600,
        " values_to_end_scope": lambda start_value: list(range(start_value, 24)),
    },
    "WY": {
        "unit_name": "weekday",
        "value_type": "list",
        "allowed_values": {
            "MO": 1,
            "TU": 2,
            "WE": 3,
            "TH": 4,
            "FR": 5,
            "SA": 6,
            "SU": 7,
        },
        "default_pattern": r"-(1|2|3|4|5|6|7)",
        "alternative_pattern": r"(MO|TU|WE|TH|FR|SA|SU)",
        "default_representation": lambda value: f"-{value}",
        "alternative_representation": lambda value: next(
            key
            for key, val in cast(Dict[str, int], UNITS["WY"]["allowed_values"]).items()
            if val == value
        ),
        "over_join_units": ["WK"],
        "under_join_units": ["HR"],
        "unit_as_seconds": 86400,
        " values_to_end_scope": lambda start_value: list(range(start_value, 8)),
    },
    "WK": {
        "unit_name": "week",
        "value_type": "range",
        "allowed_values": {"min": 1, "max": 53},
        "default_pattern": r"(-W[0-4]\d|-W5[0-3])",
        "alternative_pattern": r"(W[0-4]\d|W5[0-3])",
        "default_representation": lambda value: f"-W{value:02d}",
        "alternative_representation": lambda value: f"W{value:02d}",
        "over_join_units": ["YR"],
        "under_join_units": ["WY"],
        "unit_as_seconds": 604800,
        " values_to_end_scope": lambda start_value: list(range(start_value, 54)),
    },
    "DY": {
        "unit_name": "day",
        "value_type": "range",
        "allowed_values": {
            "Jan": {"min": 1, "max": 31},
            "Feb": {"min": 1, "max": 29},
            "Mar": {"min": 1, "max": 31},
            "Apr": {"min": 1, "max": 30},
            "May": {"min": 1, "max": 31},
            "Jun": {"min": 1, "max": 30},
            "Jul": {"min": 1, "max": 31},
            "Aug": {"min": 1, "max": 31},
            "Sep": {"min": 1, "max": 30},
            "Oct": {"min": 1, "max": 31},
            "Nov": {"min": 1, "max": 30},
            "Dec": {"min": 1, "max": 31},
        },
        "default_pattern": r"(0[1-9]|[12]\d|3[01])",
        "alternative_pattern": r"D(0[1-9]|[12]\d|3[01])",
        "default_representation": lambda value: f"{value:02d}",
        "alternative_representation": lambda value: f"D{value:02d}",
        "over_join_units": ["MH"],
        "under_join_units": ["HR"],
        "unit_as_seconds": 86400,
        " values_to_end_scope": lambda start_value, month: (
            [31]
            if month is None
            else list(
                range(
                    start_value,
                    day_allow_vals[month]["max"] + 1,
                )
            )
        ),
    },
    "MH": {
        "unit_name": "month",
        "value_type": "list",
        "allowed_values": {
            "Jan": 1,
            "Feb": 2,
            "Mar": 3,
            "Apr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Aug": 8,
            "Sep": 9,
            "Oct": 10,
            "Nov": 11,
            "Dec": 12,
        },
        "default_pattern": r"-(01|02|03|04|05|06|07|08|09|10|11|12)-",
        "alternative_pattern": (r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"),
        "default_representation": lambda value: f"-{value:02d}-",
        "alternative_representation": lambda target_value: next(
            key for key, val in month_allowed_values.items() if val == target_value
        ),
        "over_join_units": ["YR"],
        "under_join_units": ["DY"],
        "unit_as_seconds": lambda month, leap: (
            28 * 86400
            if month == "Feb" and not leap
            # fmt: off
            else (
                day_allow_vals[month]["max"] * 86400)
        ),
        # fmt: on
        " values_to_end_scope": lambda start_value: list(range(start_value, 13)),
    },
    "YR": {
        "unit_name": "year",
        "value_type": "range",
        "allowed_values": {"min": START_YEAR, "max": END_YEAR},
        "default_pattern": r"(\d{4})",
        "alternative_pattern": r"Y?(\d{4})",
        "default_representation": lambda value: f"{value:04d}",
        "alternative_representation": lambda value: f"{value:04d}",
        "over_join_units": [],
        "under_join_units": ["WK", "MH"],
        "unit_as_seconds": lambda leap: 31622400 if leap else 31536000,
        " values_to_end_scope": lambda start_value: list(
            range(start_value, END_YEAR + 1)
        ),
    },
}
