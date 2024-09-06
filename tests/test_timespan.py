# tests/test_timespan.py

import pytest
from src.configs import CombinedSequnce, PointType
from src.timepoint import TimePoint, TimePointArgumentError
from src.constants import SpanType, EdgeType, SpanContain
from src.timespan import TimeSpan, TimeSpanCreateArgumentError, TimeSpanStringError


@pytest.fixture
def valid_start_end_points():
    """
    Fixture to provide valid start and end TimePoint objects.
    """
    start = TimePoint("2022-01-01")
    end = TimePoint("2022-12-31")
    start_end_edge = TimePoint("2022-01-01T23:59:59.")
    start_start_edge = TimePoint("2022-01-01T00:00:00.")
    end_end_edge = TimePoint("2022-12-31T23:59:59.")
    end_start_edge = TimePoint("2022-12-31T00:00:00.")
    return start, end, start_start_edge, start_end_edge, end_start_edge, end_end_edge


@pytest.fixture
def valid_leap_year_points():
    """
    Fixture to provide TimePoint objects for a leap year.
    """
    start = TimePoint("2020-02-29")
    end = TimePoint("2020-03-01")
    start_end_edge = TimePoint("2020-02-29T23:59:59.")
    start_start_edge = TimePoint("2020-02-29T00:00:00.")
    end_end_edge = TimePoint("2020-03-01T23:59:59.")
    end_start_edge = TimePoint("2020-03-01T00:00:00.")

    return start, end, start_start_edge, start_end_edge, end_start_edge, end_end_edge


def test_valid_creation_with_time_points(valid_start_end_points):
    """
    Test creating a TimeSpan object with valid start and end TimePoint objects.
    """
    start, end, start_start_edge, start_end_edge, end_start_edge, end_end_edge = (
        valid_start_end_points
    )
    span_type = SpanType.BETWEEN

    try:
        timespan = TimeSpan(start=start, end=end, span_type=span_type)
    except Exception as e:
        pytest.fail(f"Unexpected exception raised: {e}")

    assert timespan.start == start_start_edge, "Start TimePoint does not match."
    assert timespan.end == end_end_edge, "End TimePoint does not match."
    assert timespan.type == SpanType.BETWEEN, "SpanType does not match."
    assert (
        timespan.start_edge == EdgeType.START
    ), "Start edge should be EdgeType.START by default."
    assert (
        timespan.end_edge == EdgeType.END
    ), "End edge should be EdgeType.END by default."
    assert timespan.sequence_combination in [
        CombinedSequnce.GRE,
    ], "Unexpected sequence combination."


def test_valid_creation_using_string():
    """
    Test creating a TimeSpan object using a valid span string.
    """
    span_str = "@2022-01-01_2022-12-31@"

    try:
        timespan = TimeSpan(start=span_str)
    except Exception as e:
        pytest.fail(f"Unexpected exception raised while parsing string: {e}")

    expected_start = TimePoint("2022-01-01T00:00:00.")
    expected_end = TimePoint("2022-12-31T23:59:59.")

    assert timespan.start == expected_start, "Parsed start TimePoint does not match."
    assert timespan.end == expected_end, "Parsed end TimePoint does not match."
    assert (
        timespan.type == SpanType.BETWEEN
    ), "SpanType should be BETWEEN for this string."
    assert timespan.start_edge == EdgeType.START, "Start edge should be EdgeType.START."
    assert timespan.end_edge == EdgeType.END, "End edge should be EdgeType.END."


def test_valid_creation_with_leap_year(valid_leap_year_points):
    """
    Test creating a TimeSpan object that includes a leap day.
    """
    start, end, start_start_edge, start_end_edge, end_start_edge, end_end_edge = (
        valid_leap_year_points
    )
    span_type = SpanType.BETWEEN

    try:
        timespan = TimeSpan(start=start, end=end, span_type=span_type)
    except Exception as e:
        pytest.fail(f"Unexpected exception raised for leap year span: {e}")

    assert (
        timespan.start == start_start_edge
    ), "Start TimePoint does not match for leap year."
    assert timespan.end == end_end_edge, "End TimePoint does not match for leap year."
    assert timespan.type == SpanType.BETWEEN, "SpanType does not match for leap year."
    assert timespan.is_leap, "TimeSpan should recognize leap year."
    assert timespan.sequence_combination in [
        CombinedSequnce.GRE,
    ], "Unexpected sequence combination for leap year."


def test_invalid_span_creation_with_reversed_time_points():
    """
    Test creating a TimeSpan object with start greater than end.
    """
    start = TimePoint("2022-12-31")
    end = TimePoint("2022-01-01")

    with pytest.raises(TimeSpanCreateArgumentError) as exc_info:
        timespan = TimeSpan(start=start, end=end, span_type=SpanType.BETWEEN)

    assert "start is greater than end" in str(
        exc_info.value
    ), "Expected error message for reversed time points."


def test_invalid_span_with_missing_start_or_end_points():
    """
    Test creating a TimeSpan object with None as start and end points.
    """
    # Case 1: start is None, end is valid
    end = TimePoint("2022-12-31")

    with pytest.raises(TimeSpanCreateArgumentError) as exc_info:
        timespan = TimeSpan(start=None, end=end, span_type=SpanType.BETWEEN)

    assert "start cannot be None" in str(
        exc_info.value
    ), "Expected error message for missing start point."

    # Case 2: end is None, start is valid
    start = TimePoint("2022-01-01")

    with pytest.raises(TimeSpanCreateArgumentError) as exc_info:
        timespan = TimeSpan(
            start=start, start_edge=EdgeType.END, end=None, span_type=SpanType.BETWEEN
        )

    assert (
        "start_edge cannot be 'EdgeType.END' when span_type is 'Sapn.Type.BETWEEN'"
        in str(exc_info.value)
    ), "Expected error message for missing end point."


def test_creation_with_scope_mismatch():
    """
    Test creating a TimeSpan object with mismatched scopes.
    """
    # Assuming TimePoint has a scope property, and that scope mismatch should raise an error.
    start = TimePoint("-01-01")
    end = TimePoint("2022-12-31")

    with pytest.raises(TimeSpanCreateArgumentError) as exc_info:
        timespan = TimeSpan(start=start, end=end, span_type=SpanType.BETWEEN)

    assert "start and end must have the same scope" in str(
        exc_info.value
    ), "Expected error message for mismatched scopes."


def test_invalid_string_format():
    """
    Test creating a TimeSpan object with an invalid string format.
    """
    span_str = "2022-12-31"  # Invalid format (missing '@')

    with pytest.raises(TimeSpanCreateArgumentError) as exc_info:
        timespan = TimeSpan(start=span_str)

    assert (
        "__init__: parse_time_span_string: TimeSpan string must start and end with '@'"
        in str(exc_info.value)
    ), "Expected error message for invalid string format."


def test_str_and_repr_for_valid_timespan():
    """
    Test the __str__ and __repr__ methods for a valid TimeSpan object.
    """
    start_pt_str = "2022-01-01"
    end_pt_str = "2022-12-31"
    start = TimePoint(start_pt_str)
    end = TimePoint(end_pt_str)
    timespan = TimeSpan(start=start, end=end, span_type=SpanType.BETWEEN)

    print(f"timespan: {timespan}\n")
    print(f"timesapn start edge: {timespan.start_edge}\n")
    print(f"timesapn end edge: {timespan.end_edge}\n")
    print(f"timesapn type: {timespan.type}\n")
    print(f"timesapn init_start: {timespan.init_start}\n")
    print(f"timesapn init_end: {timespan.init_end}\n")

    expected_str = f"S(@{start_pt_str}_{end_pt_str}@)"
    expected_repr = f"TimeSpan('@{start_pt_str}_{end_pt_str}@')"

    assert (
        str(timespan) == expected_str
    ), "__str__ method does not return the expected string format."
    assert (
        repr(timespan) == expected_repr
    ), "__repr__ method does not return the expected string format."


def test_str_and_repr_with_no_end_point():
    """
    Test the __str__ and __repr__ methods for a TimeSpan object with no end point.
    """
    start = TimePoint("2022-01-01")
    timespan = TimeSpan(start=start, span_type=SpanType.AFTER)

    expected_str = f"S(_2022-01-01@)"
    expected_repr = f"TimeSpan('_2022-01-01@')"

    assert (
        str(timespan) == expected_str
    ), "__str__ method does not handle TimeSpan with no end point correctly."
    assert (
        repr(timespan) == expected_repr
    ), "__repr__ method does not handle TimeSpan with no end point correctly."


def test_property_methods_for_timespan():
    """
    Test the property methods start, end, start_edge, end_edge, type for a valid TimeSpan object.
    """
    start = TimePoint("2022-01-01")
    end = TimePoint("2022-12-31")
    timespan = TimeSpan(start=start, end=end, span_type=SpanType.BETWEEN)

    assert (
        timespan.init_start == start
    ), "The start property does not return the correct TimePoint."
    assert (
        timespan.init_end == end
    ), "The end property does not return the correct TimePoint."
    assert (
        timespan.start_edge == EdgeType.START
    ), "The start_edge property does not return the correct EdgeType."
    assert (
        timespan.end_edge == EdgeType.END
    ), "The end_edge property does not return the correct EdgeType."
    assert (
        timespan.type == SpanType.BETWEEN
    ), "The type property does not return the correct SpanType."


def test_sequence_combination_and_is_leap():
    """
    Test the sequence_combination and is_leap properties for a leap year TimeSpan object.
    """
    start = TimePoint("2020-02-29")
    end = TimePoint("2020W18SU")
    timespan = TimeSpan(start=start, end=end, span_type=SpanType.BETWEEN)

    assert (
        timespan.is_leap
    ), "The is_leap property should return True for a leap year span."
    assert (
        timespan.sequence_combination == CombinedSequnce.ISO_GRE
    ), "The sequence_combination should return CombinedSequnce.ISO for matching ISO sequences."

    # Test with mismatched ISO and Gregorian sequences
    end_gregorian = TimePoint("2020-12-31")
    timespan_mixed = TimeSpan(
        start=start, end=end_gregorian, span_type=SpanType.BETWEEN
    )

    assert (
        timespan_mixed.sequence_combination == CombinedSequnce.GRE
    ), "The sequence_combination should return CombinedSequnce.ISO_GRE for mixed ISO and Gregorian sequences."


def test_parse_time_span_string_valid():
    """
    Test parsing a valid time span string.
    """
    span_str = "@2022-01-01_2022-12-31@"

    expected_result = {
        "start": TimePoint("2022-01-01"),
        "start_edge": EdgeType.START,
        "end": TimePoint("2022-12-31"),
        "end_edge": EdgeType.END,
        "span_type": SpanType.BETWEEN,
    }

    result = TimeSpan.parse_time_span_string(span_str)

    assert (
        result["start"] == expected_result["start"]
    ), "Start TimePoint does not match."
    assert result["end"] == expected_result["end"], "End TimePoint does not match."
    assert (
        result["start_edge"] == expected_result["start_edge"]
    ), "Start edge does not match."
    assert result["end_edge"] == expected_result["end_edge"], "End edge does not match."
    assert (
        result["span_type"] == expected_result["span_type"]
    ), "SpanType does not match."


def test_parse_time_span_string_empty():
    """
    Test parsing an empty time span string.
    """
    empty_span_str = ""

    with pytest.raises(TimeSpanStringError) as exc_info:
        TimeSpan.parse_time_span_string(empty_span_str)

    assert "TimeSpan string cannot be empty or whitespace" in str(
        exc_info.value
    ), "Expected TimeSpanStringError for empty string."


def test_occurrences_in_period_no_occurrences():
    """
    Test calculating occurrences when there are no valid occurrences in the period.
    """
    time_span = TimeSpan(
        start=TimePoint("01T12:21:21."),
        end=TimePoint("11T12:21:21."),
        span_type=SpanType.BETWEEN,
    )
    period_start = TimePoint("2022-01-01")
    period_end = TimePoint("2022-12-31")

    occurrences = TimeSpan.occurrences_in_period(time_span, period_start, period_end)

    assert occurrences == [
        TimeSpan("@2022-01-01T12:21:21._2022-01-11T12:21:21.@"),
        TimeSpan("@2022-02-01T12:21:21._2022-02-11T12:21:21.@"),
        TimeSpan("@2022-03-01T12:21:21._2022-03-11T12:21:21.@"),
        TimeSpan("@2022-04-01T12:21:21._2022-04-11T12:21:21.@"),
        TimeSpan("@2022-05-01T12:21:21._2022-05-11T12:21:21.@"),
        TimeSpan("@2022-06-01T12:21:21._2022-06-11T12:21:21.@"),
        TimeSpan("@2022-07-01T12:21:21._2022-07-11T12:21:21.@"),
        TimeSpan("@2022-08-01T12:21:21._2022-08-11T12:21:21.@"),
        TimeSpan("@2022-09-01T12:21:21._2022-09-11T12:21:21.@"),
        TimeSpan("@2022-10-01T12:21:21._2022-10-11T12:21:21.@"),
        TimeSpan("@2022-11-01T12:21:21._2022-11-11T12:21:21.@"),
        TimeSpan("@2022-12-01T12:21:21._2022-12-11T12:21:21.@"),
    ], "Occurrences should be None or an empty list when there are no valid occurrences."


def test_is_contained_in_span_valid():
    """
    Test checking if one time span is contained within another.
    """
    contained_span = TimeSpan(
        start=TimePoint("2022-03-01"),
        end=TimePoint("2022-03-31"),
        span_type=SpanType.BETWEEN,
    )
    container_span = TimeSpan(
        start=TimePoint("2022-01-01"),
        end=TimePoint("2022-12-31"),
        span_type=SpanType.BETWEEN,
    )

    containment = TimeSpan.is_contained_in_span(contained_span, container_span)

    assert (
        containment == SpanContain.INSIDE
    ), "The contained span should be fully inside the container span."


def test_is_contained_in_span_no_containment():
    """
    Test checking if one time span is not contained within another.
    """
    contained_span = TimeSpan(
        start=TimePoint("2023-02-01"),
        end=TimePoint("2023-11-29"),
        span_type=SpanType.BETWEEN,
    )
    container_span = TimeSpan(
        start=TimePoint("2022-01-01"),
        end=TimePoint("2022-12-31"),
        span_type=SpanType.BETWEEN,
    )

    containment = TimeSpan.is_contained_in_span(contained_span, container_span)

    assert (
        containment == SpanContain.AHEAD
    ), "The contained span should not be contained in the container span."


def test_handling_leap_year():
    """
    Test handling leap years for a time span starting or ending on February 29th.
    """
    # Case 1: Time span entirely within a leap year, including Feb 29
    start = TimePoint("2020-02-29")
    end = TimePoint("2020-03-01")

    try:
        timespan = TimeSpan(start=start, end=end, span_type=SpanType.BETWEEN)
    except Exception as e:
        pytest.fail(f"Unexpected exception for leap year span: {e}")

    assert (
        timespan.is_leap
    ), "The time span should be recognized as part of a leap year."
    assert (
        timespan.init_start == start
    ), "Start TimePoint does not match for leap year span."
    assert timespan.init_end == end, "End TimePoint does not match for leap year span."

    # Case 2: Comparison with a non-leap year time span
    non_leap_start = TimePoint("2019-02-28")
    non_leap_end = TimePoint("2019-03-01")

    try:
        non_leap_timespan = TimeSpan(
            start=non_leap_start, end=non_leap_end, span_type=SpanType.BETWEEN
        )
    except Exception as e:
        pytest.fail(f"Unexpected exception for non-leap year span: {e}")

    assert (
        not non_leap_timespan.is_leap
    ), "Non-leap year span should not be marked as a leap year."
    assert (
        timespan.start != non_leap_timespan.start
    ), "Leap year and non-leap year should have different start points."


def test_boundary_conditions_for_edge_types():
    """
    Test handling boundary conditions for edge types (START and END).
    """
    start = TimePoint("2022-01-01")
    end = TimePoint("2022-12-31")

    # Test with start_edge = EdgeType.START and end_edge = EdgeType.END
    try:
        timespan = TimeSpan(
            start=start,
            end=end,
            span_type=SpanType.BETWEEN,
            start_edge=EdgeType.START,
            end_edge=EdgeType.END,
        )
    except Exception as e:
        pytest.fail(f"Unexpected exception for edge conditions: {e}")

    assert timespan.start_edge == EdgeType.START, "Start edge should be EdgeType.START."
    assert timespan.end_edge == EdgeType.END, "End edge should be EdgeType.END."
    assert (
        timespan.init_start == start
    ), "Start TimePoint does not match with EdgeType.START."
    assert timespan.init_end == end, "End TimePoint does not match with EdgeType.END."


def test_invalid_scope_handling():
    """
    Test handling mismatched scopes for start and end TimePoints.
    """
    start = TimePoint("-01-01")
    end = TimePoint("2022-12-31")

    with pytest.raises(TimeSpanCreateArgumentError) as exc_info:
        TimeSpan(start=start, end=end, span_type=SpanType.BETWEEN)

    assert "start and end must have the same scope" in str(
        exc_info.value
    ), "Expected TimeSpanCreateArgumentError for mismatched scopes."
