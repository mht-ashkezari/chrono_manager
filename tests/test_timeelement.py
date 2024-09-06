import pytest
from src.timeelement import TimeElement

from src.timepoint import TimePoint

from src.constants import (
    END_POINT_GRE,
    START_DATE_ELEMENTS_GRE,
    END_DATE_ELEMENTS_GRE,
    START_DATE_ELEMENTS_ISO,
    END_DATE_ELEMENTS_ISO,
    START_POINT_GRE,
)

""" Initialization Tests """


# Test Initialization with Valid Unit Name and Value
def test_initialization_with_valid_unit_name_and_value():
    time_element = TimeElement("YR", 2024)
    assert time_element.element_unit == "YR"
    assert time_element.element_value == 2024


# Test Initialization with Valid String Representation
def test_initialization_with_valid_string_representation():
    time_element = TimeElement("Y2024")
    assert time_element.element_unit == "YR"
    assert time_element.element_value == 2024


# Test Initialization with Invalid Unit Name
def test_initialization_with_invalid_unit_name():
    with pytest.raises(ValueError, match="Invalid unit name 'INVALID'"):
        TimeElement("INVALID", 10)


# Test Initialization with Non-integer Value
def test_initialization_with_non_integer_value():
    with pytest.raises(TypeError, match="Expected 'value' to be an integer"):
        TimeElement("YR", "ten")


"""  Equality and Comparison Tests  """


# Test Equality (__eq__)
def test_equality():
    time_element_1 = TimeElement("YR", 2024)
    time_element_2 = TimeElement("YR", 2024)
    assert time_element_1 == time_element_2


# Test Inequality (__ne__)
def test_inequality():
    time_element_1 = TimeElement("YR", 2024)
    time_element_2 = TimeElement("YR", 2023)
    time_element_3 = TimeElement("MH", 12)
    assert time_element_1 != time_element_2
    assert time_element_1 != time_element_3


# Test Less Than (__lt__)
def test_less_than():
    time_element_1 = TimeElement("YR", 2023)
    time_element_2 = TimeElement("YR", 2024)
    assert time_element_1 < time_element_2


# Test Greater Than (__gt__)
def test_greater_than():
    time_element_1 = TimeElement("YR", 2025)
    time_element_2 = TimeElement("YR", 2024)
    assert time_element_1 > time_element_2


# Test Comparison with Different Units
def test_comparison_with_different_units():
    time_element_1 = TimeElement("YR", 2024)
    time_element_2 = TimeElement("MH", 12)
    with pytest.raises(
        ValueError, match="Cannot compare TimeElement objects with different units"
    ):
        time_element_1 < time_element_2


"""  String Representation Tests  """


# Test __str__ Method
def test_str_method():
    time_element = TimeElement("YR", 2024)
    assert str(time_element) == "E(YR=2024)"


# Test __repr__ Method
def test_repr_method():
    time_element = TimeElement("YR", 2024)
    assert repr(time_element) == "TimeElement('YR', 2024)"


"""  Property Tests """


# Test element_unit Property
def test_element_unit_property():
    time_element = TimeElement("YR", 2024)
    assert time_element.element_unit == "YR"


# Test element_value Property
def test_element_value_property():
    time_element = TimeElement("YR", 2024)
    assert time_element.element_value == 2024


# Test over_join_units and under_join_units Properties
def test_over_join_units_property():
    time_element = TimeElement("YR", 2024)
    # Assuming that over_join_units returns a list like ['WK', 'MH']
    expected_units = []  # Replace with actual expected units
    assert time_element.over_join_units == expected_units


def test_under_join_units_property():
    time_element = TimeElement("YR", 2024)
    # Assuming that under_join_units returns a list like []
    expected_units = ["WK", "MH"]  # Replace with actual expected units
    assert time_element.under_join_units == expected_units


# Test default_representation Property
def test_default_representation_property():
    time_element = TimeElement("YR", 2024)
    expected_representation = (
        "2024"  # Replace with the actual expected default representation
    )
    assert time_element.default_representation == expected_representation


# Test alternative_representation Property
def test_alternative_representation_property():
    time_element = TimeElement("YR", 2024)
    expected_representation = (
        "2024"  # Replace with the actual expected alternative representation
    )
    assert time_element.alternative_representation == expected_representation


"""  Static Method Tests  """


# Test get_max_value Method
def test_get_max_value():
    max_value = TimeElement.get_max_value("YR")
    assert (
        max_value == 2199
    )  # Replace with the actual maximum year value based on your implementation


# Test get_min_value Method
def test_get_min_value():
    min_value = TimeElement.get_min_value("YR")
    assert (
        min_value == 1800
    )  # Replace with the actual minimum year value based on your implementation


# Test _validate_value Method
def test_validate_value_valid():
    assert TimeElement._validate_value("YR", 2024) is True


def test_validate_value_invalid():
    with pytest.raises(ValueError, match="Invalid value '3000' for unit 'YR'"):
        TimeElement._validate_value("YR", 3000)


"""Parsing Method Tests """


# Test parse_time_string_to_elements Method with valid string
def test_parse_time_string_to_elements_valid():
    elements, matched, unmatched = TimeElement.parse_time_string_to_elements(
        "Y2024M12D31"
    )
    assert len(elements) == 3
    assert elements[0].element_unit == "YR"
    assert elements[0].element_value == 2024
    assert matched == ["Y2024", "M12", "D31"]
    assert unmatched == []


# Test parse_time_string_to_elements Method with invalid string
def test_parse_time_string_to_elements_invalid():
    elements, matched, unmatched = TimeElement.parse_time_string_to_elements(
        "InvalidString"
    )
    assert elements == []
    assert matched == []
    assert unmatched == list("InvalidString")


""" Boundary and Edge Cases  """


# Test Year Boundaries
def test_year_boundaries():
    time_element_min = TimeElement("YR", 1800)
    time_element_max = TimeElement("YR", 2199)
    assert time_element_min.element_value == 1800
    assert time_element_max.element_value == 2199


# Test Day Boundaries
def test_day_boundaries():
    time_element_min = TimeElement("DY", 1)
    time_element_max = TimeElement("DY", 31)
    assert time_element_min.element_value == 1
    assert time_element_max.element_value == 31


# Test Invalid String Patterns
def test_invalid_string_patterns():
    with pytest.raises(ValueError, match="Error validating value '9999' for unit 'YR'"):
        TimeElement.parse_time_string_to_elements("Y99999")


"""Integration Tests with Constants  """


# Test TimeElement objects in START_DATE_ELEMENTS_GRE
def test_start_date_elements_gre():
    assert len(START_DATE_ELEMENTS_GRE) == 6
    assert START_DATE_ELEMENTS_GRE[0].element_unit == "YR"
    assert START_DATE_ELEMENTS_GRE[0].element_value == 1800
    assert START_DATE_ELEMENTS_GRE[1].element_unit == "MH"
    assert START_DATE_ELEMENTS_GRE[1].element_value == 1
    assert START_DATE_ELEMENTS_GRE[2].element_unit == "DY"
    assert START_DATE_ELEMENTS_GRE[2].element_value == 1


# Test TimeElement objects in END_DATE_ELEMENTS_GRE
def test_end_date_elements_gre():
    assert len(END_DATE_ELEMENTS_GRE) == 6
    assert END_DATE_ELEMENTS_GRE[0].element_unit == "YR"
    assert END_DATE_ELEMENTS_GRE[0].element_value == 2199
    assert END_DATE_ELEMENTS_GRE[1].element_unit == "MH"
    assert END_DATE_ELEMENTS_GRE[1].element_value == 1
    assert END_DATE_ELEMENTS_GRE[2].element_unit == "DY"
    assert END_DATE_ELEMENTS_GRE[2].element_value == 1


# Test TimeElement objects in START_DATE_ELEMENTS_ISO
def test_start_date_elements_iso():
    assert len(START_DATE_ELEMENTS_ISO) == 6
    assert START_DATE_ELEMENTS_ISO[0].element_unit == "YR"
    assert START_DATE_ELEMENTS_ISO[0].element_value == 1800
    assert START_DATE_ELEMENTS_ISO[1].element_unit == "WK"
    assert START_DATE_ELEMENTS_ISO[1].element_value == 1
    assert START_DATE_ELEMENTS_ISO[2].element_unit == "WY"
    assert START_DATE_ELEMENTS_ISO[2].element_value == 3


# Test TimeElement objects in END_DATE_ELEMENTS_ISO
def test_end_date_elements_iso():
    assert len(END_DATE_ELEMENTS_ISO) == 6
    assert END_DATE_ELEMENTS_ISO[0].element_unit == "YR"
    assert END_DATE_ELEMENTS_ISO[0].element_value == 2199
    assert END_DATE_ELEMENTS_ISO[1].element_unit == "WK"
    assert END_DATE_ELEMENTS_ISO[1].element_value == 1
    assert END_DATE_ELEMENTS_ISO[2].element_unit == "WY"
    assert END_DATE_ELEMENTS_ISO[2].element_value == 3


"""Integration Tests with TimePoint"""


# Test TimePoint initialization with TimeElement objects
def test_timepoint_initialization_gre():
    time_elements = [
        TimeElement("YR", 2024),
        TimeElement("MH", 12),
        TimeElement("DY", 31),
        TimeElement("HR", 23),
        TimeElement("ME", 59),
        TimeElement("SD", 59),
    ]
    time_point = TimePoint(time_elements)
    assert len(time_point.time_elements) == 6
    assert time_point.time_elements[0].element_unit == "YR"
    assert time_point.time_elements[0].element_value == 2024
    assert time_point.year == 2024
    assert time_point.month == 12
    assert time_point.day == 31
    assert time_point.hour == 23
    assert time_point.minute == 59
    assert time_point.second == 59


# Test TimePoint integration with START_POINT_GRE
def test_start_point_gre():
    assert len(START_POINT_GRE.time_elements) == 6
    assert START_POINT_GRE.time_elements[0].element_unit == "YR"
    assert START_POINT_GRE.time_elements[0].element_value == 1800
    assert START_POINT_GRE.year == 1800


# Test TimePoint integration with END_POINT_GRE
def test_end_point_gre():
    assert len(END_POINT_GRE.time_elements) == 6
    assert END_POINT_GRE.time_elements[0].element_unit == "YR"
    assert END_POINT_GRE.time_elements[0].element_value == 2199
    assert END_POINT_GRE.time_elements[1].element_unit == "MH"
    assert END_POINT_GRE.time_elements[1].element_value == 12
    assert END_POINT_GRE.time_elements[2].element_unit == "DY"
    assert END_POINT_GRE.time_elements[2].element_value == 31
    assert END_POINT_GRE.year == 2199
    assert END_POINT_GRE.month == 12
    assert END_POINT_GRE.day == 31


# Test TimePoint string initialization with valid string representation
def test_timepoint_string_initialization():
    time_point = TimePoint("Y2024DecD31H23M59S59")
    assert len(time_point.time_elements) == 6
    assert time_point.time_elements[0].element_unit == "YR"
    assert time_point.time_elements[0].element_value == 2024
    assert time_point.time_elements[1].element_unit == "MH"
    assert time_point.time_elements[1].element_value == 12
    assert time_point.time_elements[2].element_unit == "DY"
    assert time_point.time_elements[2].element_value == 31
