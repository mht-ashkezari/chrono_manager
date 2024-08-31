import pytest
from datetime import datetime
from src.timeelement import TimeElement

# Import the functions from the utilityfuncs.py module
from src.utilityfuncs import (
    days_to_year_start_iso,
    days_to_year_start_gregorian,
    is_iso_greg_compare_consistent,
    leap_years_between,
    find_year_with_53_weeks,
    find_intersection,
    _set_complete_elements_values,
    get_element_by_unit_from_elements,
    get_value_by_unit_from_elements,
    add_element_to_elements,
    find_duplicate_units,
    get_elements_sequence,
    get_unit_index_in_elements,
    is_ordered_elements,
    add_element_to_ordered_elements,
    remove_unit_from_ordered_elements,
    update_element_in_ordered_elements,
    update_unit_in_ordered_elements,
    is_elements_leap,
    what_is_sequence,
    sort_elements_by_sequence,
    are_ordered_elements_comparable,
    find_scope_in_ordered_elements,
    check_elements_validity,
    is_valid_week_53,
    find_ordered_elements_over_under_units,
    iso_to_gregorian,
    complete_ordered_elements,
    compare_two_datetimes_ints,
    compare_two_ordered_comparable_elements,
    units_vlaues_to_ordered_elements,
    ordered_elements_default_representation,
    ordered_elements_alternative_representation,
    can_contains,
)


@pytest.mark.parametrize(
    "iso_year, iso_week, iso_weekday, expected_days",
    [
        (2023, 1, 1, 1),  # First day of the year
        (2023, 1, None, 1),  # Default to Monday
        (2023, 52, 7, 364),  # Last day of 2023 (ISO)
        (2020, 53, 7, 371),  # Leap year with week 53
    ],
)
def test_days_to_year_start_iso(iso_year, iso_week, iso_weekday, expected_days):
    result = days_to_year_start_iso(iso_year, iso_week, iso_weekday)
    assert result == expected_days, f"Expected {expected_days} but got {result}"


@pytest.mark.parametrize(
    "year, month, day, expected_days",
    [
        (2023, 1, 1, 0),  # First day of the year
        (2023, 12, 31, 364),  # Last day of 2023 (non-leap year)
        (2020, 12, 31, 365),  # Last day of 2020 (leap year)
        (2023, 6, 15, 165),  # Mid-year day
    ],
)
def test_days_to_year_start_gregorian(year, month, day, expected_days):
    result = days_to_year_start_gregorian(year, month, day)
    assert result == expected_days, f"Expected {expected_days} but got {result}"


@pytest.mark.parametrize(
    "treshold, iso_year, iso_week, iso_weekday, year, month, day, expected",
    [
        (3, 2023, 1, 1, 2023, 2, 1, True),  # Difference exceeds threshold
        (3, 2023, 1, 7, 2023, 1, 15, True),  # Difference exceeds threshold
        (3, 2023, 51, 7, 2023, 12, 31, True),  # Difference exceeds threshold
        (3, 2020, 53, 7, 2020, 11, 30, True),  # Difference exceeds threshold
        (3, 2023, 1, 1, 2023, 1, 4, False),  # Difference less than threshold
        (3, 2024, 1, 1, 2024, 1, 1, False),  # Difference less than threshold
        (3, 2022, 1, 1, 2022, 1, 3, False),  # Difference less than threshold
        (3, 2020, 53, 7, 2021, 1, 1, True),  # Difference exceeds the threshold
    ],
)
def test_is_iso_greg_compare_consistent(
    treshold, iso_year, iso_week, iso_weekday, year, month, day, expected
):
    result = is_iso_greg_compare_consistent(
        treshold, iso_year, iso_week, iso_weekday, year, month, day
    )
    assert result == expected, f"Expected {expected} but got {result}"


@pytest.mark.parametrize(
    "start_year, end_year, expected_leap_years",
    [
        (2000, 2020, [2000, 2004, 2008, 2012, 2016, 2020]),
        (1990, 2000, [1992, 1996, 2000]),
        (1900, 1904, [1904]),
        (1800, 1804, [1804]),
        (2100, 2100, []),  # 2100 is not a leap year
    ],
)
def test_leap_years_between(start_year, end_year, expected_leap_years):
    result = leap_years_between(start_year, end_year)
    assert (
        result == expected_leap_years
    ), f"Expected {expected_leap_years} but got {result}"


@pytest.mark.parametrize(
    "start_year, end_year, expected_years_with_53_weeks",
    [
        (2000, 2020, [2004, 2009, 2015, 2020]),
        (1990, 2000, [1992, 1998]),
        (2100, 2100, []),  # Edge case where year 2100 has no 53 weeks
    ],
)
def test_find_year_with_53_weeks(start_year, end_year, expected_years_with_53_weeks):
    result = find_year_with_53_weeks(start_year, end_year)
    assert (
        result == expected_years_with_53_weeks
    ), f"Expected {expected_years_with_53_weeks} but got {result}"


@pytest.mark.parametrize(
    "intlist1, intlist2, expected_intersection",
    [
        ([1, 2, 3], [2, 3, 4], [2, 3]),
        ([1, 2, 3], None, [1, 2, 3]),
        (None, [2, 3, 4], [2, 3, 4]),
        ([1, 2, 3], [4, 5, 6], []),
        (None, None, None),
    ],
)
def test_find_intersection(intlist1, intlist2, expected_intersection):
    result = find_intersection(intlist1, intlist2)
    assert (
        result == expected_intersection
    ), f"Expected {expected_intersection} but got {result}"


@pytest.mark.parametrize(
    "complete_elements, default_unit_values, expected_output",
    [
        ([1, "X", 3, "X", 5, "X"], [10, 20, 30, 40, 50, 60], [1, 20, 3, 40, 5, 60]),
        (
            ["X", "X", "X", "X", "X", "X"],
            [10, 20, 30, 40, 50, 60],
            [10, 20, 30, 40, 50, 60],
        ),
        (
            [1, 2, 3, 4, 5, 6],
            [10, 20, 30, 40, 50, 60],
            [1, 2, 3, 4, 5, 6],
        ),  # No replacements needed
    ],
)
def test_set_complete_elements_values(
    complete_elements, default_unit_values, expected_output
):
    result = _set_complete_elements_values(complete_elements, default_unit_values)
    assert result == expected_output, f"Expected {expected_output} but got {result}"


@pytest.mark.parametrize(
    "unit_name, elements, expected_element",
    [
        (
            "YR",
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            TimeElement("YR", 2023),
        ),
        ("MH", [TimeElement("YR", 2023), TimeElement("MH", 8)], TimeElement("MH", 8)),
        (
            "DY",
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            None,
        ),  # Unit not present
    ],
)
def test_get_element_by_unit_from_elements(unit_name, elements, expected_element):
    result = get_element_by_unit_from_elements(unit_name, elements)
    assert result == expected_element, f"Expected {expected_element} but got {result}"


@pytest.mark.parametrize(
    "unit_name, elements, expected_value_and_index",
    [
        ("YR", [TimeElement("YR", 2023), TimeElement("MH", 8)], (2023, 0)),
        ("MH", [TimeElement("YR", 2023), TimeElement("MH", 8)], (8, 1)),
        (
            "DY",
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            (None, None),
        ),  # Unit not present
    ],
)
def test_get_value_by_unit_from_elements(unit_name, elements, expected_value_and_index):
    result = get_value_by_unit_from_elements(unit_name, elements)
    assert (
        result == expected_value_and_index
    ), f"Expected {expected_value_and_index} but got {result}"


@pytest.mark.parametrize(
    "element_added, elements, expected_output",
    [
        (
            TimeElement("DY", 15),
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
        ),
        (
            TimeElement("MH", 8),
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            None,
        ),  # Duplicate unit
        (
            TimeElement("YR", 2023),
            [],
            [TimeElement("YR", 2023)],
        ),  # Adding to an empty list
    ],
)
def test_add_element_to_elements(element_added, elements, expected_output):
    result = add_element_to_elements(element_added, elements)
    assert result == expected_output, f"Expected {expected_output} but got {result}"


@pytest.mark.parametrize(
    "elements, expected_duplicates",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("YR", 2024)],
            ["YR"],
        ),
        ([TimeElement("YR", 2023), TimeElement("MH", 8)], []),
        ([], []),  # Empty list should have no duplicates
    ],
)
def test_find_duplicate_units(elements, expected_duplicates):
    result = find_duplicate_units(elements)
    assert (
        result == expected_duplicates
    ), f"Expected {expected_duplicates} but got {result}"


@pytest.mark.parametrize(
    "elements, expected_sequence",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            ("YR", "MH", "DY", "HR", "ME", "SD"),
        ),
        (
            [TimeElement("YR", 2023), TimeElement("WK", 1), TimeElement("WY", 3)],
            ("YR", "WK", "WY", "HR", "ME", "SD"),
        ),
        (
            [TimeElement("MH", 8), TimeElement("DY", 15)],
            ("YR", "MH", "DY", "HR", "ME", "SD"),
        ),  # Partial sequence match
        (
            [TimeElement("HR", 12), TimeElement("ME", 30)],
            ("YR", "MH", "DY", "HR", "ME", "SD"),
        ),  # No full sequence
    ],
)
def test_get_elements_sequence(elements, expected_sequence):
    result = get_elements_sequence(elements)
    assert result == expected_sequence, f"Expected {expected_sequence} but got {result}"


@pytest.mark.parametrize(
    "unit_name, elements, expected_index",
    [
        ("YR", [TimeElement("YR", 2023), TimeElement("MH", 8)], 0),
        ("MH", [TimeElement("YR", 2023), TimeElement("MH", 8)], 1),
        (
            "DY",
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            None,
        ),  # Unit not present
    ],
)
def test_get_unit_index_in_elements(unit_name, elements, expected_index):
    result = get_unit_index_in_elements(unit_name, elements)
    assert result == expected_index, f"Expected {expected_index} but got {result}"


@pytest.mark.parametrize(
    "elements, expected_result",
    [
        ([TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)], True),
        (
            [TimeElement("YR", 2023), TimeElement("DY", 15), TimeElement("MH", 8)],
            False,
        ),  # Out of order
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("MH", 12)],
            False,
        ),  # Duplicate units
    ],
)
def test_is_ordered_elements(elements, expected_result):
    if expected_result:
        assert is_ordered_elements(elements) == expected_result
    else:
        with pytest.raises(ValueError):
            is_ordered_elements(elements)


@pytest.mark.parametrize(
    "element_added, elements, expected_output",
    [
        (
            TimeElement("DY", 15),
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
        ),
        (
            TimeElement("MH", 8),
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            None,
        ),  # Duplicate unit
        (
            TimeElement("YR", 2023),
            [],
            [TimeElement("YR", 2023)],
        ),  # Adding to an empty list
    ],
)
def test_add_element_to_ordered_elements(element_added, elements, expected_output):
    if expected_output is None:
        with pytest.raises(ValueError):
            add_element_to_ordered_elements(element_added, elements)
    else:
        result = add_element_to_ordered_elements(element_added, elements)
        assert result == expected_output, f"Expected {expected_output} but got {result}"


@pytest.mark.parametrize(
    "unit_removed, elements, expected_output",
    [
        (
            "DY",
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
        ),
        (
            "ME",
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            None,
        ),
        (
            "MH",
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            None,
        ),
        (
            "MH",
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            [TimeElement("YR", 2023)],
        ),
        ("MH", [TimeElement("MH", 8)], None),  # Removing the only unit
        (
            "MH",
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            [TimeElement("YR", 2023)],
        ),  # Not first or last unit
    ],
)
def test_remove_unit_from_ordered_elements(unit_removed, elements, expected_output):
    if expected_output is None:
        with pytest.raises(ValueError):
            remove_unit_from_ordered_elements(unit_removed, elements)
    else:
        result = remove_unit_from_ordered_elements(unit_removed, elements)
        assert result == expected_output, f"Expected {expected_output} but got {result}"


@pytest.mark.parametrize(
    "element_updated, elements, expected_output",
    [
        (
            TimeElement("DY", 8),
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 8)],
        ),
        (
            TimeElement("DY", 21),
            [TimeElement("YR", 2023), TimeElement("WK", 10)],
            None,
        ),  # Unit not present
        (
            TimeElement("YR", 2026),
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            [TimeElement("YR", 2026), TimeElement("MH", 8)],
        ),
        (
            TimeElement("MH", 9),
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            [TimeElement("YR", 2023), TimeElement("MH", 9)],
        ),
    ],
)
def test_update_element_in_ordered_elements(element_updated, elements, expected_output):
    if expected_output is None:
        with pytest.raises(ValueError):
            update_element_in_ordered_elements(element_updated, elements)
    else:
        result = update_element_in_ordered_elements(element_updated, elements)
        assert result == expected_output, f"Expected {expected_output} but got {result}"


@pytest.mark.parametrize(
    "unit_updated, value_updated, elements, expected_output",
    [
        (
            "MH",
            9,
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            [TimeElement("YR", 2023), TimeElement("MH", 9)],
        ),
        (
            "DY",
            15,
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 10)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
        ),
        (
            "MH",
            8,
            [TimeElement("YR", 2023), TimeElement("DY", 10)],
            None,
        ),  # Unit not present
    ],
)
def test_update_unit_in_ordered_elements(
    unit_updated, value_updated, elements, expected_output
):
    if expected_output is None:
        with pytest.raises(ValueError):
            update_unit_in_ordered_elements(unit_updated, value_updated, elements)
    else:
        result = update_unit_in_ordered_elements(unit_updated, value_updated, elements)
        assert result == expected_output, f"Expected {expected_output} but got {result}"


@pytest.mark.parametrize(
    "elements, expected_result",
    [
        (
            [TimeElement("YR", 2020), TimeElement("MH", 2), TimeElement("DY", 29)],
            True,
        ),  # Leap year
        (
            [TimeElement("YR", 2021), TimeElement("MH", 2), TimeElement("DY", 28)],
            False,
        ),  # Non-leap year
        (
            [TimeElement("MH", 2), TimeElement("DY", 29)],
            True,
        ),  # Feb 29th without year, assumed leap
    ],
)
def test_is_elements_leap(elements, expected_result):
    result = is_elements_leap(elements)
    assert result == expected_result, f"Expected {expected_result} but got {result}"


@pytest.mark.parametrize(
    "elements, expected_sequence",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            "gre",
        ),  # Gregorian sequence
        (
            [TimeElement("YR", 2023), TimeElement("WK", 1), TimeElement("WY", 3)],
            "iso",
        ),  # ISO sequence
        (
            [TimeElement("HR", 12), TimeElement("ME", 30)],
            "gre",
        ),  # Gregorian sequence
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("WY", 5)],
            None,
        ),  # No Valid sequence
    ],
)
def test_what_is_sequence(elements, expected_sequence):
    result = what_is_sequence(elements)
    assert result == expected_sequence, f"Expected {expected_sequence} but got {result}"


@pytest.mark.parametrize(
    "elements, expected_sorted_elements, expected_missing",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            [],
        ),
        (
            [TimeElement("DY", 15), TimeElement("MH", 8)],
            [TimeElement("MH", 8), TimeElement("DY", 15)],
            [],
        ),  # Missing year
        ([TimeElement("WK", 12), TimeElement("DY", 30)], None, []),  # No valid sequence
    ],
)
def test_sort_elements_by_sequence(
    elements, expected_sorted_elements, expected_missing
):
    result, missing = sort_elements_by_sequence(elements)
    assert (
        result == expected_sorted_elements
    ), f"Expected {expected_sorted_elements} but got {result}"
    assert (
        missing == expected_missing
    ), f"Expected missing {expected_missing} but got {missing}"


@pytest.mark.parametrize(
    "elements1, elements2, expected_comparable",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 16)],
            True,
        ),  # Comparable dates
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            [TimeElement("YR", 2023), TimeElement("WK", 15)],
            True,
        ),  # Incompatible sequences
        (
            [TimeElement("MH", 8), TimeElement("DY", 22)],
            [TimeElement("WK", 8), TimeElement("WY", 3)],
            True,
        ),
        (
            [TimeElement("DY", 20), TimeElement("HR", 1)],
            [TimeElement("WY", 2), TimeElement("HR", 3)],
            False,
        ),  # Comparable ISO elements
    ],
)
def test_are_ordered_elements_comparable(elements1, elements2, expected_comparable):
    result = are_ordered_elements_comparable(elements1, elements2)
    assert (
        result == expected_comparable
    ), f"Expected {expected_comparable} but got {result}"


@pytest.mark.parametrize(
    "elements, expected_scope",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            None,
        ),  # None scope before Year
        ([TimeElement("WK", 1), TimeElement("WY", 3)], "YR"),  # Scope is Year
        ([TimeElement("HR", 12), TimeElement("ME", 12)], "DY"),  # Scope is Day
        ([TimeElement("WY", 5), TimeElement("HR", 23)], "WK"),  # Scope is Week
        ([TimeElement("YR", 2023)], None),  # No scope before Year
    ],
)
def test_find_scope_in_ordered_elements(elements, expected_scope):
    result = find_scope_in_ordered_elements(elements)
    assert result == expected_scope, f"Expected {expected_scope} but got {result}"


@pytest.mark.parametrize(
    "elements, should_raise_error",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 2), TimeElement("DY", 28)],
            False,
        ),  # Valid non-leap year date
        (
            [TimeElement("YR", 2020), TimeElement("MH", 2), TimeElement("DY", 29)],
            False,
        ),  # Valid leap year date
        (
            [TimeElement("YR", 2021), TimeElement("MH", 2), TimeElement("DY", 29)],
            True,
        ),  # Invalid non-leap year date
        (
            [TimeElement("YR", 2023), TimeElement("WK", 53), TimeElement("WY", 7)],
            True,
        ),  # Invalid week 53 for non-leap year
    ],
)
def test_check_elements_validity(elements, should_raise_error):
    if should_raise_error:
        with pytest.raises(ValueError):
            check_elements_validity(elements)
    else:
        assert check_elements_validity(elements) is True


@pytest.mark.parametrize(
    "year, expected_result",
    [
        (2020, True),  # Leap year with 53 weeks
        (2021, False),  # Non-leap year without 53 weeks
        (2009, True),  # A year with 53 weeks
    ],
)
def test_is_valid_week_53(year, expected_result):
    result = is_valid_week_53(year)
    assert result == expected_result, f"Expected {expected_result} but got {result}"


@pytest.mark.parametrize(
    "elements, expected_over_under",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            {"O": [], "U": ["HR", "ME", "SD"]},
        ),  # Over and under elements
        (
            [TimeElement("WK", 1), TimeElement("WY", 1)],
            {"O": ["YR"], "U": ["HR", "ME", "SD"]},
        ),  # Week units with over/under
        (
            [TimeElement("HR", 12), TimeElement("ME", 30)],
            {"O": ["YR", "MH", "DY"], "U": ["SD"]},
        ),  # Hour and minute with over/under
    ],
)
def test_find_ordered_elements_over_under_units(elements, expected_over_under):
    result = find_ordered_elements_over_under_units(elements)
    assert (
        result == expected_over_under
    ), f"Expected {expected_over_under} but got {result}"


@pytest.mark.parametrize(
    "year, week, weekday, hour, minute, second, expected_gregorian",
    [
        (2023, 1, 1, 0, 0, 0, datetime(2023, 1, 2, 0, 0, 0)),  # First ISO week of 2023
        (
            2020,
            53,
            7,
            23,
            59,
            59,
            datetime(2021, 1, 3, 23, 59, 59),
        ),  # Last day of ISO week 53 in 2020
        (
            2021,
            52,
            3,
            12,
            0,
            0,
            datetime(2021, 12, 29, 12, 0, 0),
        ),  # Middle of ISO week 52 in 2021
        (2021, 53, 1, 0, 0, 0, None),  # Invalid ISO week 53 in 2021
    ],
)
def test_iso_to_gregorian(
    year, week, weekday, hour, minute, second, expected_gregorian
):
    result = iso_to_gregorian(year, week, weekday, hour, minute, second)
    assert (
        result == expected_gregorian
    ), f"Expected {expected_gregorian} but got {result}"


@pytest.mark.parametrize(
    "elements, expected_complete_elements",
    [
        (
            [TimeElement("MH", 8), TimeElement("DY", 15)],
            ["O", 8, 15, "U", "U", "U"],
        ),  # Incomplete with placeholders
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            [2023, 8, 15, "U", "U", "U"],
        ),  # Complete Gregorian
        (
            [TimeElement("WK", 53), TimeElement("WY", 7)],
            ["O", 53, 7, "U", "U", "U"],
        ),  # ISO week
    ],
)
def test_complete_ordered_elements(elements, expected_complete_elements):
    result = complete_ordered_elements(elements)
    assert (
        result == expected_complete_elements
    ), f"Expected {expected_complete_elements} but got {result}"


@pytest.mark.parametrize(
    "element_ints1, is_iso1, element_ints2, is_iso2, expected_result",
    [
        (
            [2023, 1, 1, 0, 0, 0],
            False,
            [2023, 1, 1, 0, 0, 0],
            False,
            0,
        ),  # Identical Gregorian dates
        (
            [2023, 1, 1, 0, 0, 0],
            False,
            [2023, 1, 2, 0, 0, 0],
            False,
            -1,
        ),  # First date earlier
        (
            [2023, 1, 1, 0, 0, 0],
            False,
            [2023, 1, 1, 0, 0, 1],
            False,
            -1,
        ),  # First date earlier by one second
        (
            [2023, 1, 2, 0, 0, 0],
            False,
            [2023, 1, 1, 0, 0, 0],
            False,
            1,
        ),  # First date later
        (
            [2023, 1, 1, 0, 0, 0],
            True,
            [2023, 1, 2, 0, 0, 0],
            False,
            0,
        ),  # Mixed ISO and Gregorian, first earlier
        (
            [2023, 1, 1, 0, 0, 0],
            True,
            [2023, 1, 1, 0, 0, 0],
            False,
            1,
        ),  # Mixed ISO and Gregorian, identical
    ],
)
def test_compare_two_datetimes_ints(
    element_ints1, is_iso1, element_ints2, is_iso2, expected_result
):
    result = compare_two_datetimes_ints(element_ints1, is_iso1, element_ints2, is_iso2)
    assert result == expected_result, f"Expected {expected_result} but got {result}"


@pytest.mark.parametrize(
    "elements1, elements2, expected_result",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            0,
        ),  # Identical dates
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 16)],
            -1,
        ),  # First date earlier
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 17)],
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 16)],
            1,
        ),  # First date later
        (
            [TimeElement("YR", 2020), TimeElement("MH", 2), TimeElement("DY", 29)],
            [TimeElement("YR", 2020), TimeElement("MH", 2), TimeElement("DY", 28)],
            1,
        ),  # Leap year comparison
    ],
)
def test_compare_two_ordered_comparable_elements(elements1, elements2, expected_result):
    result = compare_two_ordered_comparable_elements(elements1, elements2)
    if isinstance(result, dict):
        assert result["greater"] == [2020] if expected_result == 1 else []
        assert result["less"] == [2020] if expected_result == -1 else []
        assert result["equal"] == [2020] if expected_result == 0 else []
    else:
        assert result == expected_result, f"Expected {expected_result} but got {result}"


@pytest.mark.parametrize(
    "year, month, day, hour, minute, second, is_iso, expected_elements",
    [
        (
            2023,
            8,
            15,
            12,
            0,
            0,
            False,
            [
                TimeElement("YR", 2023),
                TimeElement("MH", 8),
                TimeElement("DY", 15),
                TimeElement("HR", 12),
                TimeElement("ME", 0),
                TimeElement("SD", 0),
            ],
        ),
        (
            None,
            53,
            7,
            None,
            None,
            None,
            True,
            [TimeElement("WK", 53), TimeElement("WY", 7)],
        ),  # ISO Week/Weekday only
        (
            None,
            38,
            None,
            None,
            None,
            None,
            False,
            None,  # Expected to raise ValueError
        ),  # Incorrect TimeElement instance
    ],
)
def test_units_vlaues_to_ordered_elements(
    year, month, day, hour, minute, second, is_iso, expected_elements
):
    if expected_elements is None:
        with pytest.raises(ValueError):
            units_vlaues_to_ordered_elements(
                year, month, day, hour, minute, second, is_iso
            )
    else:
        result = units_vlaues_to_ordered_elements(
            year, month, day, hour, minute, second, is_iso
        )
        assert (
            result == expected_elements
        ), f"Expected {expected_elements} but got {result}"


@pytest.mark.parametrize(
    "elements, expected_representation",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            "2023-08-15",
        ),  # Default representation
        (
            [TimeElement("WK", 53), TimeElement("WY", 7)],
            "-W53-7",
        ),  # ISO Week representation
    ],
)
def test_ordered_elements_default_representation(elements, expected_representation):
    result = ordered_elements_default_representation(elements)
    assert (
        result == expected_representation
    ), f"Expected {expected_representation} but got {result}"


@pytest.mark.parametrize(
    "elements, expected_representation",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            "2023AugD15",
        ),  # Alternative representation
        (
            [TimeElement("WK", 53), TimeElement("WY", 7)],
            "W53SU",
        ),  # ISO Week with Sunday
    ],
)
def test_ordered_elements_alternative_representation(elements, expected_representation):
    result = ordered_elements_alternative_representation(elements)
    assert (
        result == expected_representation
    ), f"Expected {expected_representation} but got {result}"


@pytest.mark.parametrize(
    "container, contained, expected_result",
    [
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8), TimeElement("DY", 15)],
            [TimeElement("MH", 8), TimeElement("DY", 15)],
            False,
        ),  # Containment
        (
            [TimeElement("YR", 2022), TimeElement("WK", 7)],
            [TimeElement("WY", 7)],
            True,
        ),  # ISO Week containment
        (
            [TimeElement("YR", 2023), TimeElement("MH", 8)],
            [TimeElement("DY", 15)],
            True,
        ),  # Non-containment
    ],
)
def test_can_contains(container, contained, expected_result):
    result = can_contains(container, contained)
    assert result == expected_result, f"Expected {expected_result} but got {result}"
