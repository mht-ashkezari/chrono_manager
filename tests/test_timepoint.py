import pytest
from src.timepoint import (
    TimePoint,
    TimePointError,
    TimePointCreationError,
    TimePointArgumentError,
    TimePointNotComparableError,
    TimePointAttributeSetError,
    TimePointNotSpanError,
    TimePointOccurrenceError,
)
from src.configs import START_SCOPE_ELEMENTS_GRE, END_SCOPE_ELEMENTS_GRE
from src.timeelement import TimeElement


# Sample valid TimeElement data for tests
valid_elements = [
    TimeElement("YR", 2023),
    TimeElement("MH", 8),
    TimeElement("DY", 29),
]

valid_string = "2023-08-29"

invalid_string_no_elements = ""
invalid_string_unmatched_substr = "2023-08-29_extra"

missing_units_elements = [
    TimeElement("YR", 2023),
    TimeElement("DY", 8),
    # Missing day element
]

unsorted_elements = [
    TimeElement("MH", 8),
    TimeElement("DY", 29),
    TimeElement("YR", 2023),
]


@pytest.mark.parametrize(
    "elements, expected_year, expected_month, expected_day",
    [(valid_elements, 2023, 8, 29)],
)
def test_init_with_valid_elements(
    elements, expected_year, expected_month, expected_day
):
    time_point = TimePoint(elements)
    assert time_point.time_elements == elements
    assert time_point.year == expected_year
    assert time_point.month == expected_month
    assert time_point.day == expected_day


@pytest.mark.parametrize(
    "time_string, expected_length, expected_year, expected_month, expected_day",
    [("2023-08-29", 3, 2023, 8, 29), ("2023Sep29", 3, 2023, 9, 29)],
)
def test_init_with_valid_string(
    time_string, expected_length, expected_year, expected_month, expected_day
):
    time_point = TimePoint(time_string)
    assert len(time_point.time_elements) == expected_length
    assert time_point.year == expected_year
    assert time_point.month == expected_month
    assert time_point.day == expected_day


@pytest.mark.parametrize(
    "time_string, expected_length, expected_year, expected_month, expected_day, expected_hour, expected_minute, expected_second",
    [
        ("2023-08-29", 3, 2023, 8, 29, None, None, None),
        ("2023-08-29T15:30:45.", 6, 2023, 8, 29, 15, 30, 45),
        ("Y2024Aug12T23:53:30.", 6, 2024, 8, 12, 23, 53, 30),
    ],
)
def test_init_with_full_valid_string(
    time_string,
    expected_length,
    expected_year,
    expected_month,
    expected_day,
    expected_hour,
    expected_minute,
    expected_second,
):
    time_point = TimePoint(time_string)
    assert len(time_point.time_elements) == expected_length
    assert time_point.year == expected_year
    assert time_point.month == expected_month
    assert time_point.day == expected_day
    assert time_point.hour == expected_hour
    assert time_point.minute == expected_minute
    assert time_point.second == expected_second


@pytest.mark.parametrize(
    "time_string, expected_length, expected_year, expected_week, expected_weekday, expected_hour, expected_minute, expected_second",
    [
        ("2023W34-5", 3, 2023, 34, 5, None, None, None),
        ("W34TUT12:30", 4, None, 34, 2, 12, 30, None),
        ("-5T23:53:30.", 4, None, None, 5, 23, 53, 30),
    ],
)
def test_init_with_iso_valid_string(
    time_string,
    expected_length,
    expected_year,
    expected_week,
    expected_weekday,
    expected_hour,
    expected_minute,
    expected_second,
):
    time_point = TimePoint(time_string)
    assert len(time_point.time_elements) == expected_length
    assert time_point.year == expected_year
    assert time_point.week == expected_week
    assert time_point.weekday == expected_weekday
    assert time_point.hour == expected_hour
    assert time_point.minute == expected_minute
    assert time_point.second == expected_second


@pytest.mark.parametrize(
    "invalid_string, expected_error_message",
    [
        (
            "",
            "String argument has no valid elements",
        ),
        (
            "2023-08-29_extra",
            "Invalid argument: String argument has unmatched substring: ['_', 'e', 'x', 't', 'r', 'a']",
        ),
    ],
)
def test_init_with_invalid_string(invalid_string, expected_error_message):
    with pytest.raises(TimePointArgumentError) as exc_info:
        TimePoint(invalid_string)
    assert expected_error_message in str(exc_info.value)


@pytest.mark.parametrize(
    "invalid_elements, expected_error",
    [
        (
            [
                TimeElement("YR", 2023),
                TimeElement("MH", 2),
                TimeElement("DY", 30),
            ],  # Invalid date (Feb 30th does not exist)
            TimePointCreationError,
        ),
        (
            [
                TimeElement("YR", 2023),
                TimeElement("DY", 30),
            ],
            TimePointArgumentError,
        ),  # Missing units
    ],
)
def test_init_with_invalid_elements(invalid_elements, expected_error):
    with pytest.raises(expected_error):
        TimePoint(invalid_elements)


# Sample valid TimeElement data for tests
valid_elements_gre = [
    TimeElement("YR", 2023),
    TimeElement("MH", 8),
    TimeElement("DY", 29),
    TimeElement("HR", 15),
    TimeElement("ME", 30),
    TimeElement("SD", 45),
]

valid_elements_iso = [
    TimeElement("YR", 2023),
    TimeElement("WK", 34),
    TimeElement("WY", 5),
    TimeElement("HR", 15),
    TimeElement("ME", 30),
    TimeElement("SD", 45),
]


@pytest.mark.parametrize("elements, expected_year", [(valid_elements_gre, 2023)])
def test_year_property(elements, expected_year):
    time_point = TimePoint(elements)
    assert time_point.year == expected_year


@pytest.mark.parametrize("elements, expected_month", [(valid_elements_gre, 8)])
def test_month_property(elements, expected_month):
    time_point = TimePoint(elements)
    assert time_point.month == expected_month


@pytest.mark.parametrize("elements, expected_week", [(valid_elements_iso, 34)])
def test_week_property(elements, expected_week):
    time_point = TimePoint(elements)
    assert time_point.week == expected_week


@pytest.mark.parametrize("elements, expected_day", [(valid_elements_gre, 29)])
def test_day_property(elements, expected_day):
    time_point = TimePoint(elements)
    assert time_point.day == expected_day


@pytest.mark.parametrize("elements, expected_weekday", [(valid_elements_iso, 5)])
def test_weekday_property(elements, expected_weekday):
    time_point = TimePoint(elements)
    assert time_point.weekday == expected_weekday


@pytest.mark.parametrize("elements, expected_hour", [(valid_elements_gre, 15)])
def test_hour_property(elements, expected_hour):
    time_point = TimePoint(elements)
    assert time_point.hour == expected_hour


@pytest.mark.parametrize("elements, expected_minute", [(valid_elements_gre, 30)])
def test_minute_property(elements, expected_minute):
    time_point = TimePoint(elements)
    assert time_point.minute == expected_minute


@pytest.mark.parametrize("elements, expected_second", [(valid_elements_gre, 45)])
def test_second_property(elements, expected_second):
    time_point = TimePoint(elements)
    assert time_point.second == expected_second


@pytest.mark.parametrize(
    "elements, expected_scope",
    [
        (
            [
                TimeElement("DY", 5),
                TimeElement("HR", 15),
                TimeElement("ME", 30),
                TimeElement("SD", 45),
            ],
            "MH",
        ),  # Gregorian scope
        (
            [
                TimeElement("WY", 5),
                TimeElement("HR", 15),
                TimeElement("ME", 30),
                TimeElement("SD", 45),
            ],
            "WK",
        ),  # ISO scope
    ],
)
def test_scope_property(elements, expected_scope):
    time_point = TimePoint(elements)
    assert time_point.scope == expected_scope


@pytest.mark.parametrize(
    "elements, is_iso", [(valid_elements_gre, False), (valid_elements_iso, True)]
)
def test_is_iso_property(elements, is_iso):
    time_point = TimePoint(elements)
    assert time_point.is_iso == is_iso


@pytest.mark.parametrize(
    "elements, is_leap",
    [
        (valid_elements_gre, False),  # 2023 is not a leap year
        (
            [TimeElement("YR", 2024), TimeElement("MH", 2), TimeElement("DY", 29)],
            True,
        ),  # 2024 is a leap year
    ],
)
def test_is_leap_property(elements, is_leap):
    time_point = TimePoint(elements)
    assert time_point.is_leap == is_leap


@pytest.mark.parametrize("elements, expected_over_units", [(valid_elements_gre, [])])
def test_over_units_property(elements, expected_over_units):
    time_point = TimePoint(elements)
    assert time_point.over_units == expected_over_units


@pytest.mark.parametrize(
    "elements, expected_under_units",
    [
        (
            [
                TimeElement("YR", 2023),
                TimeElement("MH", 8),
                TimeElement("DY", 29),
            ],
            ["HR", "ME", "SD"],
        )
    ],
)
def test_under_units_property(elements, expected_under_units):
    time_point = TimePoint(elements)
    assert time_point.under_units == expected_under_units


@pytest.mark.parametrize(
    "elements, expected_start_scope",
    [(valid_elements_gre, list(START_SCOPE_ELEMENTS_GRE))],
)
def test_start_point_in_scope_property_gregorian(elements, expected_start_scope):
    time_point = TimePoint(elements)
    assert time_point.start_point_in_scope.time_elements == expected_start_scope


@pytest.mark.parametrize(
    "elements, expected_end_scope", [(valid_elements_gre, list(END_SCOPE_ELEMENTS_GRE))]
)
def test_end_point_in_scope_property_gregorian(elements, expected_end_scope):
    time_point = TimePoint(elements)
    assert time_point.end_point_in_scope.time_elements == expected_end_scope


@pytest.mark.parametrize(
    "elements, expected_start_elements",
    [
        (
            [
                TimeElement("YR", 2023),
                TimeElement("MH", 8),
                TimeElement("DY", 29),
            ],
            [
                TimeElement("YR", 2023),
                TimeElement("MH", 8),
                TimeElement("DY", 29),
                TimeElement("HR", 0),
                TimeElement("ME", 0),
                TimeElement("SD", 0),
            ],
        )
    ],
)
def test_start_point_property(elements, expected_start_elements):
    time_point = TimePoint(elements)
    assert time_point.start_point.time_elements == expected_start_elements


@pytest.mark.parametrize(
    "elements, expected_end_elements",
    [
        (
            [
                TimeElement("YR", 2023),
                TimeElement("MH", 8),
                TimeElement("DY", 29),
            ],
            [
                TimeElement("YR", 2023),
                TimeElement("MH", 8),
                TimeElement("DY", 29),
                TimeElement("HR", 23),
                TimeElement("ME", 59),
                TimeElement("SD", 59),
            ],
        )
    ],
)
def test_end_point_property(elements, expected_end_elements):
    time_point = TimePoint(elements)
    assert time_point.end_point.time_elements == expected_end_elements


# Sample valid TimeElement data for tests
elements1 = [
    TimeElement("YR", 2023),
    TimeElement("MH", 8),
    TimeElement("DY", 29),
]

elements2 = [
    TimeElement("YR", 2023),
    TimeElement("MH", 8),
    TimeElement("DY", 29),
]

elements3 = [
    TimeElement("YR", 2023),
    TimeElement("MH", 9),
    TimeElement("DY", 1),
]

# ISO elements
iso_elements1 = [
    TimeElement("YR", 2023),
    TimeElement("WK", 34),
    TimeElement("WY", 5),
]

iso_elements2 = [
    TimeElement("YR", 2023),
    TimeElement("WK", 34),
    TimeElement("WY", 6),
]

# Equality and Hashing Tests


@pytest.mark.parametrize(
    "elements1, elements2, expected",
    [(elements1, elements2, True), (elements1, elements3, False)],
)
def test_eq_method(elements1, elements2, expected):
    time_point1 = TimePoint(elements1)
    time_point2 = TimePoint(elements2)
    assert (time_point1 == time_point2) == expected


@pytest.mark.parametrize(
    "elements1, elements2, expected",
    [(elements1, elements2, True), (elements1, elements3, False)],
)
def test_hash_method(elements1, elements2, expected):
    time_point1 = TimePoint(elements1)
    time_point2 = TimePoint(elements2)
    assert (hash(time_point1) == hash(time_point2)) == expected


# Static Method Tests


@pytest.mark.parametrize(
    "time_point_elements, start_point_elements, end_point_elements, expected",
    [
        (
            [
                TimeElement("YR", 2023),
                TimeElement("MH", 8),
                TimeElement("DY", 29),
            ],
            [TimeElement("YR", 2022), TimeElement("MH", 4), TimeElement("DY", 30)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 31)],
            0,
        ),
        (
            [TimeElement("YR", 2023), TimeElement("MH", 7), TimeElement("DY", 31)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 1)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 31)],
            -1,
        ),
        (
            [TimeElement("YR", 2023), TimeElement("MH", 9), TimeElement("DY", 1)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 1)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 31)],
            1,
        ),
    ],
)
def test_is_between_points(
    time_point_elements, start_point_elements, end_point_elements, expected
):
    time_point = TimePoint(time_point_elements)
    start_point = TimePoint(start_point_elements)
    end_point = TimePoint(end_point_elements)
    assert TimePoint.is_between_points(time_point, start_point, end_point) == expected


def test_is_between_points_not_comparable():
    with pytest.raises(TimePointNotComparableError):
        time_point = TimePoint(
            [
                TimeElement("YR", 2023),
                TimeElement("MH", 8),
                TimeElement("DY", 29),
            ]
        )
        start_point = TimePoint(
            [
                TimeElement("WK", 34),
                TimeElement("WY", 5),
            ]
        )
        end_point = TimePoint(
            [
                TimeElement("YR", 2023),
                TimeElement("WK", 34),
            ]
        )
        TimePoint.is_between_points(time_point, start_point, end_point)


@pytest.mark.parametrize(
    "point, overs_starts, overs_ends, expected",
    [
        (
            TimePoint(
                [
                    TimeElement("DY", 20),
                    TimeElement("HR", 22),
                ]
            ),
            [2020, 8],
            [2022, 4],
            [
                TimePoint("2020-08-20T22:00:00."),
                TimePoint("2020-09-20T22:00:00."),
                TimePoint("2020-10-20T22:00:00."),
                TimePoint("2020-11-20T22:00:00."),
                TimePoint("2020-12-20T22:00:00."),
                TimePoint("2021-01-20T22:00:00."),
                TimePoint("2021-02-20T22:00:00."),
                TimePoint("2021-03-20T22:00:00."),
                TimePoint("2021-04-20T22:00:00."),
                TimePoint("2021-05-20T22:00:00."),
                TimePoint("2021-06-20T22:00:00."),
                TimePoint("2021-07-20T22:00:00."),
                TimePoint("2021-08-20T22:00:00."),
                TimePoint("2021-09-20T22:00:00."),
                TimePoint("2021-10-20T22:00:00."),
                TimePoint("2021-11-20T22:00:00."),
                TimePoint("2021-12-20T22:00:00."),
                TimePoint("2022-01-20T22:00:00."),
                TimePoint("2022-02-20T22:00:00."),
                TimePoint("2022-03-20T22:00:00."),
                TimePoint("2022-04-20T22:00:00."),
            ],
        )
    ],
)
def test_points_occurances_in_over_range(point, overs_starts, overs_ends, expected):
    result = TimePoint._points_occurances_in_over_range(point, overs_starts, overs_ends)
    assert result == expected


@pytest.mark.parametrize(
    "time_point_elements, start_point_elements, end_point_elements, expected_occurrences",
    [
        (
            [
                TimeElement("DY", 20),
                TimeElement("HR", 22),
            ],
            [TimeElement("YR", 2020), TimeElement("MH", 8), TimeElement("DY", 1)],
            [TimeElement("YR", 2022), TimeElement("MH", 4), TimeElement("DY", 28)],
            [
                TimePoint("2020-08-20T22:00:00."),
                TimePoint("2020-09-20T22:00:00."),
                TimePoint("2020-10-20T22:00:00."),
                TimePoint("2020-11-20T22:00:00."),
                TimePoint("2020-12-20T22:00:00."),
                TimePoint("2021-01-20T22:00:00."),
                TimePoint("2021-02-20T22:00:00."),
                TimePoint("2021-03-20T22:00:00."),
                TimePoint("2021-04-20T22:00:00."),
                TimePoint("2021-05-20T22:00:00."),
                TimePoint("2021-06-20T22:00:00."),
                TimePoint("2021-07-20T22:00:00."),
                TimePoint("2021-08-20T22:00:00."),
                TimePoint("2021-09-20T22:00:00."),
                TimePoint("2021-10-20T22:00:00."),
                TimePoint("2021-11-20T22:00:00."),
                TimePoint("2021-12-20T22:00:00."),
                TimePoint("2022-01-20T22:00:00."),
                TimePoint("2022-02-20T22:00:00."),
                TimePoint("2022-03-20T22:00:00."),
                TimePoint("2022-04-20T22:00:00."),
            ],
        ),
    ],
)
def test_occurrences_in_period(
    time_point_elements,
    start_point_elements,
    end_point_elements,
    expected_occurrences,
):
    time_point = TimePoint(time_point_elements)
    start_point = TimePoint(start_point_elements)
    end_point = TimePoint(end_point_elements)
    occurrences = TimePoint.occurrences_in_period(time_point, start_point, end_point)

    assert occurrences == expected_occurrences


# Sample valid and invalid TimeElement data for tests
valid_elements = [
    TimeElement("YR", 2023),
    TimeElement("MH", 8),
    TimeElement("DY", 28),
]

invalid_elements = [
    TimeElement("YR", 2023),
    TimeElement("MH", 2),
    TimeElement("DY", 30),  # Invalid date (Feb 30th does not exist)
]

valid_string = "2023-08-29"
invalid_string = "2023-15-99"  # Invalid month and day


@pytest.mark.parametrize(
    "exception_class, exception_message, trigger_func",
    [
        (
            TimePointError,
            "General TimePoint error",
            lambda: raise_exception(TimePointError, "General TimePoint error"),
        ),
        (
            TimePointCreationError,
            "Error creating TimePoint instance: Creation error occurred",
            lambda: raise_exception(TimePointCreationError, "Creation error occurred"),
        ),
        (
            TimePointArgumentError,
            "Invalid argument: Invalid argument passed",
            lambda: raise_exception(TimePointArgumentError, "Invalid argument passed"),
        ),
        (
            TimePointNotComparableError,
            "TimePoint instances are not comparable",
            lambda: raise_exception(
                TimePointNotComparableError,
                TimePoint([TimeElement("MH", 10), TimeElement("DY", 12)]),
                TimePoint([TimeElement("DY", 10), TimeElement("HR", 12)]),
            ),
        ),
        (
            TimePointAttributeSetError,
            "Error setting attribute 'year' with value '2023'",
            lambda: raise_exception(TimePointAttributeSetError, "year", 2023),
        ),
        (
            TimePointNotSpanError,
            f"there is no span between {TimePoint(valid_elements)} and {TimePoint(valid_elements)}",
            lambda: raise_exception(
                TimePointNotSpanError,
                TimePoint(valid_elements),
                TimePoint(valid_elements),
            ),
        ),
        (
            TimePointOccurrenceError,
            "Error in calculating occurrences: Invalid occurrence calculation",
            lambda: raise_exception(
                TimePointOccurrenceError, "Invalid occurrence calculation"
            ),
        ),
    ],
)
def test_exceptions(exception_class, exception_message, trigger_func):
    with pytest.raises(exception_class) as exc_info:
        trigger_func()
    assert exception_message in str(exc_info.value)


def raise_exception(exception_class, *args):
    raise exception_class(*args)


@pytest.mark.parametrize(
    "invalid_elements, expected_exception",
    [
        (invalid_elements, TimePointCreationError),
    ],
)
def test_time_point_creation_error_invalid_elements(
    invalid_elements, expected_exception
):
    with pytest.raises(expected_exception) as exc_info:
        TimePoint(invalid_elements)
    assert "Error in creating TimePoint instance" in str(exc_info.value)


@pytest.mark.parametrize(
    "invalid_string, expected_exception",
    [
        ("2023-15-99", TimePointArgumentError),
    ],
)
def test_time_point_argument_error_invalid_string(invalid_string, expected_exception):
    with pytest.raises(expected_exception) as exc_info:
        TimePoint(invalid_string)
    assert "Invalid argument: String argument has unmatched substring: ['-', '-', '9', '9']" in str(
        exc_info.value
    ) or "argument(str) has no valid elements" in str(
        exc_info.value
    )


def test_time_point_not_span_error_trigger():
    time_point1 = TimePoint(
        [
            TimeElement("YR", 2023),
            TimeElement("MH", 8),
            TimeElement("DY", 29),
        ]
    )
    time_point2 = TimePoint(
        [
            TimeElement("YR", 2023),
            TimeElement("MH", 8),
            TimeElement("DY", 29),
        ]
    )
    with pytest.raises(TimePointNotSpanError) as exc_info:
        TimePoint.is_between_points(time_point1, time_point2, time_point1)
    assert "there is no span between" in str(exc_info.value)


def test_time_point_occurrence_error_trigger():
    time_point1 = TimePoint([TimeElement("YR", 2022)])
    time_point2 = TimePoint([TimeElement("YR", 2022)])
    time_point3 = TimePoint([TimeElement("DY", 25)])
    with pytest.raises(TimePointOccurrenceError) as exc_info:
        TimePoint.occurrences_in_period(time_point3, time_point2, time_point2)
    assert "Error in calculating occurrences" in str(exc_info.value)
