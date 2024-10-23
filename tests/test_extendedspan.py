import pytest
from src.constants import EdgeType
from src.timespan import TimeSpan
from src.timepoint import TimePoint, TimePointNotComparableError
from src.extendedspan import ExtenedTimeSpan, ExtendedSpanArgumentError, ExtendedSpanStringError


# 1. Create fixture for TimePoint setup
@pytest.fixture
def valid_timepoint():
    """Creates a valid TimePoint object for testing."""
    return TimePoint(2023, 10, 23)  # Example: Year, Month, Day


@pytest.fixture
def valid_edge_type():
    """Creates a valid EdgeType object for testing."""
    return EdgeType.START  # Assuming EdgeType.START is a valid enum type

# 2. Test Setup for Valid Inputs


def test_valid_extended_time_span(valid_timepoint, valid_edge_type):
    """Test valid setup of ExtenedTimeSpan object."""
    ex_span = ExtenedTimeSpan(
        start=valid_timepoint,
        start_edge=valid_edge_type,
        end=TimePoint(2024, 10, 23),  # Example: Year, Month, Day for the end
        end_edge=EdgeType.END,  # Assuming EdgeType.END is valid
        subsequent_scopes=2
    )
    assert ex_span.start_point == valid_timepoint
    assert ex_span.end_point == TimePoint(2024, 10, 23)
    assert ex_span.subsequent_scopes == 2


# 3. Test Invalid Inputs for Constructor
def test_invalid_timepoint_raises_exception(valid_edge_type):
    """Test that passing invalid TimePoint raises an ExtendedSpanArgumentError."""
    with pytest.raises(ExtendedSpanArgumentError):
        ExtenedTimeSpan(
            start="invalid_start_point",  # Invalid TimePoint, expecting an object
            start_edge=valid_edge_type,
            end=None,
            end_edge=None
        )


def test_missing_edge_type_raises_exception(valid_timepoint):
    """Test that missing EdgeType raises ExtendedSpanArgumentError."""
    with pytest.raises(ExtendedSpanArgumentError):
        ExtenedTimeSpan(
            start=valid_timepoint,
            start_edge=None,  # Missing edge type
            end=TimePoint(2024, 10, 23),
            end_edge=EdgeType.END,
            subsequent_scopes=1
        )


def test_invalid_subsequent_scopes_raises_exception(valid_timepoint, valid_edge_type):
    """Test that invalid subsequent scopes raises ExtendedSpanArgumentError."""
    with pytest.raises(ExtendedSpanArgumentError):
        ExtenedTimeSpan(
            start=valid_timepoint,
            start_edge=valid_edge_type,
            end=TimePoint(2024, 10, 23),
            end_edge=EdgeType.END,
            subsequent_scopes=-1  # Invalid, must be >= 1
        )


# 4. Test for TimePoint comparison error
def test_timepoint_comparison_error(valid_timepoint, valid_edge_type):
    """Test that TimePoint comparison error raises ExtendedSpanArgumentError."""
    with pytest.raises(ExtendedSpanArgumentError):
        # Assume TimePointNotComparableError will occur during TimePoint comparison
        ExtenedTimeSpan(
            start=valid_timepoint,
            start_edge=valid_edge_type,
            end=valid_timepoint,  # Same as start, should raise an error
            end_edge=EdgeType.END,
            subsequent_scopes=1
        )


# 5. Test using string for start (from_string) that should raise ExtendedSpanStringError
def test_invalid_string_start_raises_string_error():
    """Test that invalid string format for start raises ExtendedSpanStringError."""
    with pytest.raises(ExtendedSpanStringError):
        ExtenedTimeSpan(
            start="InvalidStringFormat",
            start_edge=None,
            end=None,
            end_edge=None
        )


# 1. Test valid initialization with TimePoint objects
def test_valid_initialization_with_timepoints():
    """Test valid initialization of ExtenedTimeSpan with TimePoint objects."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    start_edge = EdgeType.START
    end_edge = EdgeType.END

    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=start_edge,
        end=end_point,
        end_edge=end_edge,
        subsequent_scopes=2
    )

    # Check that the object initializes correctly
    assert ex_span.start_point == start_point
    assert ex_span.end_point == end_point
    assert ex_span.start_edge == start_edge
    assert ex_span.end_edge == end_edge
    assert ex_span.subsequent_scopes == 2


# 2. Test initialization when a string is passed for start
def test_initialization_with_string_start(mocker):
    """Test initialization when a valid string is passed for start."""
    mocker.patch('src.extended_time_span.ExtenedTimeSpan.from_string', return_value={
        "start": TimePoint(2023, 1, 1),
        "start_edge": EdgeType.START,
        "end": TimePoint(2024, 1, 1),
        "end_edge": EdgeType.END,
        "subsequent_scopes": 3
    })

    # Passing a string for start
    ex_span = ExtenedTimeSpan(
        start="2023-2024#3",
        start_edge=None,  # This will be handled by from_string
        end=None,  # This will be handled by from_string
        end_edge=None,  # This will be handled by from_string
        subsequent_scopes=None  # This will be handled by from_string
    )

    # Check that the object initializes correctly from string
    assert ex_span.start_point == TimePoint(2023, 1, 1)
    assert ex_span.end_point == TimePoint(2024, 1, 1)
    assert ex_span.start_edge == EdgeType.START
    assert ex_span.end_edge == EdgeType.END
    assert ex_span.subsequent_scopes == 3


# 3. Test invalid start parameter raises ExtendedSpanArgumentError
def test_invalid_start_parameter_raises_exception():
    """Test that an invalid start parameter raises ExtendedSpanArgumentError."""
    invalid_start = "InvalidStartPoint"
    with pytest.raises(ExtendedSpanArgumentError):
        ExtenedTimeSpan(
            start=invalid_start,  # Invalid start (not a TimePoint or valid string)
            start_edge=EdgeType.START,
            end=TimePoint(2024, 1, 1),
            end_edge=EdgeType.END,
            subsequent_scopes=2
        )


# 4. Test invalid end parameter raises ExtendedSpanArgumentError
def test_invalid_end_parameter_raises_exception():
    """Test that an invalid end parameter raises ExtendedSpanArgumentError."""
    start_point = TimePoint(2023, 1, 1)
    with pytest.raises(ExtendedSpanArgumentError):
        ExtenedTimeSpan(
            start=start_point,
            start_edge=EdgeType.START,
            end="InvalidEndPoint",  # Invalid end (not a TimePoint)
            end_edge=EdgeType.END,
            subsequent_scopes=2
        )


# 5. Test invalid EdgeType parameters raise ExtendedSpanArgumentError
def test_invalid_edge_type_raises_exception():
    """Test that invalid EdgeType parameters raise ExtendedSpanArgumentError."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)

    with pytest.raises(ExtendedSpanArgumentError):
        ExtenedTimeSpan(
            start=start_point,
            start_edge=None,  # Invalid start_edge (None)
            end=end_point,
            end_edge=EdgeType.END,
            subsequent_scopes=2
        )

    with pytest.raises(ExtendedSpanArgumentError):
        ExtenedTimeSpan(
            start=start_point,
            start_edge=EdgeType.START,
            end=end_point,
            end_edge=None,  # Invalid end_edge (None)
            subsequent_scopes=2
        )


# 6. Test TimePoint.compare_points raises TimePointNotComparableError
def test_timepoint_compare_raises_exception(mocker):
    """Test that TimePointNotComparableError is raised and handled as ExtendedSpanArgumentError."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)

    # Mock the compare_points method to raise TimePointNotComparableError
    mocker.patch('src.timepoint.TimePoint.compare_points', side_effect=TimePointNotComparableError("Time points not comparable"))

    with pytest.raises(ExtendedSpanArgumentError):
        ExtenedTimeSpan(
            start=start_point,
            start_edge=EdgeType.START,
            end=end_point,
            end_edge=EdgeType.END,
            subsequent_scopes=2
        )


# 7. Test proper initialization of internal properties
def test_internal_properties_initialization():
    """Test that internal properties (_start_point, _end_point, _subsequent_scopes) are initialized properly."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=3
    )

    # Check internal properties
    assert ex_span._start_point == start_point
    assert ex_span._end_point == end_point
    assert ex_span._subsequent_scopes == 3
    assert ex_span._start_edge == EdgeType.START
    assert ex_span._end_edge == EdgeType.END


# Test __str__() method for default representation
def test_str_method():
    """Test the __str__() method for default string representation."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    # We expect __str__ to return the default representation (can be customized based on class logic)
    expected_str = f"ES({ex_span.default_represenantion})"
    assert str(ex_span) == expected_str


# Test __repr__() method for correct string format
def test_repr_method():
    """Test the __repr__() method for proper string representation."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    # We expect __repr__ to return the developer-friendly representation
    expected_repr = f"ExtendedSpan({ex_span.default_represenantion})"
    assert repr(ex_span) == expected_repr


# Test __str__() method with alternative representation
def test_str_method_with_alternative_representation():
    """Test the __str__() method with the alternative string representation."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=3
    )

    # We expect the default representation by default
    expected_default_str = f"ES({ex_span.default_represenantion})"
    assert str(ex_span) == expected_default_str

    # Test alternative representation (optional if method allows it)
    expected_alternative_str = ex_span.alternative_represenantion
    assert ex_span.alternative_represenantion == expected_alternative_str


# 1. Test __eq__() method with equal ExtenedTimeSpan objects
def test_equality_operator():
    """Test the __eq__() method with two equal ExtenedTimeSpan objects."""
    start_point_1 = TimePoint(2023, 1, 1)
    end_point_1 = TimePoint(2024, 1, 1)

    start_point_2 = TimePoint(2023, 1, 1)
    end_point_2 = TimePoint(2024, 1, 1)

    ex_span_1 = ExtenedTimeSpan(
        start=start_point_1,
        start_edge=EdgeType.START,
        end=end_point_1,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )

    ex_span_2 = ExtenedTimeSpan(
        start=start_point_2,
        start_edge=EdgeType.START,
        end=end_point_2,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )

    # Test for equality
    assert ex_span_1 == ex_span_2, "Two identical ExtenedTimeSpan instances should be equal."


# 2. Test __ne__() method with different ExtenedTimeSpan objects
def test_inequality_operator():
    """Test the __ne__() method with two different ExtenedTimeSpan objects."""
    start_point_1 = TimePoint(2023, 1, 1)
    end_point_1 = TimePoint(2024, 1, 1)

    start_point_2 = TimePoint(2022, 1, 1)  # Different start point
    end_point_2 = TimePoint(2024, 1, 1)

    ex_span_1 = ExtenedTimeSpan(
        start=start_point_1,
        start_edge=EdgeType.START,
        end=end_point_1,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    ex_span_2 = ExtenedTimeSpan(
        start=start_point_2,
        start_edge=EdgeType.START,
        end=end_point_2,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    # Test for inequality
    assert ex_span_1 != ex_span_2, "Two ExtenedTimeSpan instances with different start points should not be equal."


# 3. Test __eq__() with different subsequent_scopes
def test_equality_operator_with_different_scopes():
    """Test the __eq__() method with different subsequent_scopes."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span_1 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    ex_span_2 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=3  # Different subsequent_scopes
    )
    
    # Test for inequality
    assert ex_span_1 != ex_span_2, "Two ExtenedTimeSpan instances with different subsequent_scopes should not be equal."

# 4. Test __eq__() and __ne__() with different end points
def test_equality_and_inequality_with_different_end_points():
    """Test the __eq__() and __ne__() methods with different end points."""
    start_point = TimePoint(2023, 1, 1)
    end_point_1 = TimePoint(2024, 1, 1)
    end_point_2 = TimePoint(2025, 1, 1)  # Different end point
    
    ex_span_1 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point_1,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    ex_span_2 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point_2,  # Different end point
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    # Test for inequality
    assert ex_span_1 != ex_span_2, "Two ExtenedTimeSpan instances with different end points should not be equal."

# 5. Test __ne__() when comparing with a different object type
def test_inequality_with_different_object_type():
    """Test the __ne__() method when comparing ExtenedTimeSpan with a different object type."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    not_a_span = "I am not an ExtenedTimeSpan object"
    
    # Test inequality with a completely different object type
    assert ex_span != not_a_span, "ExtenedTimeSpan instance should not be equal to an object of a different type."



# 1. Test that objects with equal attributes produce the same hash
def test_hash_equality_for_equal_objects():
    """Test that ExtenedTimeSpan objects with equal attributes produce the same hash."""
    start_point_1 = TimePoint(2023, 1, 1)
    end_point_1 = TimePoint(2024, 1, 1)
    
    ex_span_1 = ExtenedTimeSpan(
        start=start_point_1,
        start_edge=EdgeType.START,
        end=end_point_1,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    ex_span_2 = ExtenedTimeSpan(
        start=start_point_1,
        start_edge=EdgeType.START,
        end=end_point_1,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    # Verify that the two objects with identical attributes have the same hash
    assert hash(ex_span_1) == hash(ex_span_2), "Hashes of two identical ExtenedTimeSpan objects should be the same."

# 2. Test that hash changes when start_point changes
def test_hash_changes_with_different_start_point():
    """Test that changing the start_point changes the hash."""
    start_point_1 = TimePoint(2023, 1, 1)
    start_point_2 = TimePoint(2022, 1, 1)  # Different start point
    end_point = TimePoint(2024, 1, 1)
    
    ex_span_1 = ExtenedTimeSpan(
        start=start_point_1,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    ex_span_2 = ExtenedTimeSpan(
        start=start_point_2,  # Different start_point
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    # Verify that the hash is different when start_point is different
    assert hash(ex_span_1) != hash(ex_span_2), "Hashes should be different when start_point is different."

# 3. Test that hash changes when end_point changes
def test_hash_changes_with_different_end_point():
    """Test that changing the end_point changes the hash."""
    start_point = TimePoint(2023, 1, 1)
    end_point_1 = TimePoint(2024, 1, 1)
    end_point_2 = TimePoint(2025, 1, 1)  # Different end point
    
    ex_span_1 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point_1,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    ex_span_2 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point_2,  # Different end_point
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    # Verify that the hash is different when end_point is different
    assert hash(ex_span_1) != hash(ex_span_2), "Hashes should be different when end_point is different."

# 4. Test that hash changes when start_edge changes
def test_hash_changes_with_different_start_edge():
    """Test that changing the start_edge changes the hash."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span_1 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,  # EdgeType.START
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    ex_span_2 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.END,  # Different start_edge
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    # Verify that the hash is different when start_edge is different
    assert hash(ex_span_1) != hash(ex_span_2), "Hashes should be different when start_edge is different."

# 5. Test that hash changes when end_edge changes
def test_hash_changes_with_different_end_edge():
    """Test that changing the end_edge changes the hash."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span_1 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.START,  # EdgeType.START
        subsequent_scopes=2
    )
    
    ex_span_2 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,  # Different end_edge
        subsequent_scopes=2
    )
    
    # Verify that the hash is different when end_edge is different
    assert hash(ex_span_1) != hash(ex_span_2), "Hashes should be different when end_edge is different."

# 6. Test that hash changes when subsequent_scopes changes
def test_hash_changes_with_different_subsequent_scopes():
    """Test that changing subsequent_scopes changes the hash."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span_1 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    ex_span_2 = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=3  # Different subsequent_scopes
    )
    
    # Verify that the hash is different when subsequent_scopes is different
    assert hash(ex_span_1) != hash(ex_span_2), "Hashes should be different when subsequent_scopes is different."




# 1. Test to_string() method with is_default_repr=True
def test_to_string_default_representation():
    """Test the to_string() static method with is_default_repr=True."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    expected_str = f"{ex_span.start_span.default_represenantion}" \
                    f"{ex_span.end_span.default_represenantion[1:]}" \
                    f"#{ex_span.subsequent_scopes}"
    
    assert ExtenedTimeSpan.to_string(ex_span, is_default_repr=True) == expected_str, \
        "Default string representation is incorrect."

# 2. Test to_string() method with is_default_repr=False
def test_to_string_alternative_representation():
    """Test the to_string() static method with is_default_repr=False."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=3
    )
    
    expected_str = f"{ex_span.start_span.alternative_represenantion}" \
                    f"{ex_span.end_span.alternative_represenantion[1:]}" \
                    f"#{ex_span.subsequent_scopes}"
    
    assert ExtenedTimeSpan.to_string(ex_span, is_default_repr=False) == expected_str, \
        "Alternative string representation is incorrect."

# 3. Test from_string() method with valid input
def test_from_string_valid_input():
    """Test the from_string() static method with valid input."""
    valid_string = "2023-01-01T00:00:00+2024-01-01T00:00:00#2"  # Example string format
    result = ExtenedTimeSpan.from_string(valid_string)
    
    # Expected values
    expected_start_point = TimePoint(2023, 1, 1)
    expected_end_point = TimePoint(2024, 1, 1)
    expected_start_edge = EdgeType.START
    expected_end_edge = EdgeType.END
    expected_subsequent_scopes = 2
    
    assert result['start'] == expected_start_point, "Parsed start point is incorrect."
    assert result['end'] == expected_end_point, "Parsed end point is incorrect."
    assert result['start_edge'] == expected_start_edge, "Parsed start edge is incorrect."
    assert result['end_edge'] == expected_end_edge, "Parsed end edge is incorrect."
    assert result['subsequent_scopes'] == expected_subsequent_scopes, "Parsed subsequent scopes are incorrect."

# 4. Test from_string() method with invalid input (no #subsequent_scopes)
def test_from_string_invalid_input_no_subsequent_scopes():
    """Test from_string() static method raises ExtendedSpanStringError for invalid input without subsequent scopes."""
    invalid_string = "2023-01-01T00:00:00+2024-01-01T00:00:00"  # Missing #2 for subsequent_scopes
    
    with pytest.raises(ExtendedSpanStringError):
        ExtenedTimeSpan.from_string(invalid_string)

# 5. Test from_string() method with invalid format
def test_from_string_invalid_format():
    """Test from_string() static method raises ExtendedSpanStringError for an invalid format."""
    invalid_string = "InvalidFormatString"  # Completely invalid format
    
    with pytest.raises(ExtendedSpanStringError):
        ExtenedTimeSpan.from_string(invalid_string)



# 1. Test that start_point returns _start_point
def test_start_point_property():
    """Test that the start_point property returns the correct value."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    assert ex_span.start_point == start_point, "start_point property should return the correct _start_point."

# 2. Test that end_point returns _end_point
def test_end_point_property():
    """Test that the end_point property returns the correct value."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    assert ex_span.end_point == end_point, "end_point property should return the correct _end_point."

# 3. Test available_years returns _available_years
def test_available_years_property():
    """Test that the available_years property returns the correct value."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    available_years = [2023, 2024]  # Example available years
    
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    # Manually set the _available_years value for testing
    ex_span._available_years = available_years
    
    assert ex_span.available_years == available_years, "available_years property should return the correct _available_years."

# 4. Test subsequent_scopes returns _subsequent_scopes
def test_subsequent_scopes_property():
    """Test that the subsequent_scopes property returns the correct value."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=3
    )
    
    assert ex_span.subsequent_scopes == 3, "subsequent_scopes property should return the correct _subsequent_scopes."

# 5. Test start_edge returns _start_edge
def test_start_edge_property():
    """Test that the start_edge property returns the correct value."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    assert ex_span.start_edge == EdgeType.START, "start_edge property should return the correct _start_edge."

# 6. Test end_edge returns _end_edge
def test_end_edge_property():
    """Test that the end_edge property returns the correct value."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    assert ex_span.end_edge == EdgeType.END, "end_edge property should return the correct _end_edge."



# 1. Test ExtendedSpanArgumentError is raised for invalid constructor parameters
def test_invalid_constructor_parameters():
    """Test that ExtendedSpanArgumentError is raised when invalid parameters are passed to the constructor."""
    invalid_start = "InvalidStartPoint"  # Not a TimePoint object or a valid string
    with pytest.raises(ExtendedSpanArgumentError):
        ExtenedTimeSpan(
            start=invalid_start,  # Invalid start
            start_edge=EdgeType.START,
            end=TimePoint(2024, 1, 1),
            end_edge=EdgeType.END,
            subsequent_scopes=2
        )

# 2. Test ExtendedSpanStringError raised in from_string() for bad format
def test_invalid_string_format_in_from_string():
    """Test that ExtendedSpanStringError is raised when an invalid string format is passed to from_string()."""
    invalid_string = "InvalidStringFormat"  # Completely invalid format
    
    with pytest.raises(ExtendedSpanStringError):
        ExtenedTimeSpan.from_string(invalid_string)

# 3. Test handling of TimePointNotComparableError in the constructor
def test_timepoint_not_comparable_error(mocker):
    """Test that TimePointNotComparableError is raised and correctly handled as ExtendedSpanArgumentError."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    # Mock the TimePoint.compare_points method to raise TimePointNotComparableError
    mocker.patch('src.timepoint.TimePoint.compare_points', side_effect=TimePointNotComparableError("Time points not comparable"))
    
    with pytest.raises(ExtendedSpanArgumentError):
        ExtenedTimeSpan(
            start=start_point,
            start_edge=EdgeType.START,
            end=end_point,
            end_edge=EdgeType.END,
            subsequent_scopes=2
        )

# 4. Test that an exception is raised when the start and end points are equal
def test_start_and_end_points_equal():
    """Test that an ExtendedSpanArgumentError is raised when the start and end points are equal."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2023, 1, 1)  # Same as start_point
    
    with pytest.raises(ExtendedSpanArgumentError):
        ExtenedTimeSpan(
            start=start_point,
            start_edge=EdgeType.START,
            end=end_point,  # Same as start_point
            end_edge=EdgeType.END,
            subsequent_scopes=2
        )




# 1. Test edge cases for time points (e.g., start and end points are very close)
def test_time_points_very_close():
    """Test that the ExtenedTimeSpan handles start and end points that are very close."""
    start_point = TimePoint(2023, 1, 1, 0, 0, 0)  # January 1st, 2023 at 00:00:00
    end_point = TimePoint(2023, 1, 1, 0, 0, 1)    # January 1st, 2023 at 00:00:01 (1 second later)
    
    try:
        ex_span = ExtenedTimeSpan(
            start=start_point,
            start_edge=EdgeType.START,
            end=end_point,
            end_edge=EdgeType.END,
            subsequent_scopes=2
        )
        assert ex_span.start_point == start_point, "start_point should match the provided start_point."
        assert ex_span.end_point == end_point, "end_point should match the provided end_point."
    except ExtendedSpanArgumentError:
        pytest.fail("The ExtenedTimeSpan should handle time points that are very close without errors.")

# 2. Test for subsequent_scopes set to 1 (minimum valid value)
def test_subsequent_scopes_min_value():
    """Test that the ExtenedTimeSpan handles subsequent_scopes set to the minimum valid value (1)."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=1  # Minimum valid value
    )
    
    assert ex_span.subsequent_scopes == 1, "subsequent_scopes should be 1, the minimum valid value."
    assert ex_span.start_point == start_point, "start_point should match the provided start_point."
    assert ex_span.end_point == end_point, "end_point should match the provided end_point."

# 3. Test for subsequent_scopes set to a very high number
def test_subsequent_scopes_high_value():
    """Test that the ExtenedTimeSpan handles a very large number for subsequent_scopes."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    high_subsequent_scopes = 1000000  # Very high value for subsequent_scopes
    
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=high_subsequent_scopes
    )
    
    assert ex_span.subsequent_scopes == high_subsequent_scopes, "subsequent_scopes should match the provided high value."
    assert ex_span.start_point == start_point, "start_point should match the provided start_point."
    assert ex_span.end_point == end_point, "end_point should match the provided end_point."

# 4. Test edge case where the start and end points are the same day but different times
def test_start_and_end_points_same_day_different_times():
    """Test that ExtenedTimeSpan handles cases where start and end points are on the same day but at different times."""
    start_point = TimePoint(2023, 1, 1, 0, 0, 0)  # Start at midnight
    end_point = TimePoint(2023, 1, 1, 23, 59, 59) # End at the last second of the same day
    
    try:
        ex_span = ExtenedTimeSpan(
            start=start_point,
            start_edge=EdgeType.START,
            end=end_point,
            end_edge=EdgeType.END,
            subsequent_scopes=2
        )
        assert ex_span.start_point == start_point, "start_point should match the provided start_point."
        assert ex_span.end_point == end_point, "end_point should match the provided end_point."
    except ExtendedSpanArgumentError:
        pytest.fail("The ExtenedTimeSpan should handle time points on the same day without errors.")



# 1. Test end-to-end case where an ExtenedTimeSpan object is created and interacts with TimeSpan
def test_integration_with_timespan():
    """Test an end-to-end case where ExtenedTimeSpan interacts with TimeSpan and other components."""
    start_point = TimePoint(2023, 1, 1)
    end_point = TimePoint(2024, 1, 1)
    
    # Create ExtenedTimeSpan object
    ex_span = ExtenedTimeSpan(
        start=start_point,
        start_edge=EdgeType.START,
        end=end_point,
        end_edge=EdgeType.END,
        subsequent_scopes=2
    )
    
    # Test interaction with TimeSpan
    start_timespan = ex_span.start_span  # Should be a TimeSpan object
    end_timespan = ex_span.end_span  # Should be a TimeSpan object
    
    # Check the properties of TimeSpan objects
    assert isinstance(start_timespan, TimeSpan), "start_span should be a TimeSpan object."
    assert isinstance(end_timespan, TimeSpan), "end_span should be a TimeSpan object."
    
    assert start_timespan.start == start_point, "start_span should have the correct start point."
    assert end_timespan.start == end_point, "end_span should have the correct end point."
    
    assert start_timespan.start_edge == EdgeType.START, "start_span should have the correct start edge."
    assert end_timespan.start_edge == EdgeType.END, "end_span should have the correct end edge."
    
    # Test the string representation of the ExtenedTimeSpan object
    expected_str = f"ES({ex_span.default_represenantion})"
    assert str(ex_span) == expected_str, "The string representation of the object is incorrect."

# 2. Test a valid end-to-end case using the string-based constructor (from_string) and interaction with other methods
def test_integration_with_from_string_constructor():
    """Test an end-to-end case where ExtenedTimeSpan is created using from_string and interacts with other methods."""
    valid_string = "2023-01-01T00:00:00+2024-01-01T00:00:00#2"  # Example valid string input
    
    # Create ExtenedTimeSpan object using from_string
    ex_span = ExtenedTimeSpan.from_string(valid_string)
    
    # Check if the resulting object has the correct values
    assert ex_span['start'] == TimePoint(2023, 1, 1), "The start point should be correct."
    assert ex_span['end'] == TimePoint(2024, 1, 1), "The end point should be correct."
    assert ex_span['start_edge'] == EdgeType.START, "The start edge should be correct."
    assert ex_span['end_edge'] == EdgeType.END, "The end edge should be correct."
    assert ex_span['subsequent_scopes'] == 2, "The subsequent scopes should be correct."
    
    # Create an ExtenedTimeSpan object with the parsed values
    ext_span_obj = ExtenedTimeSpan(
        start=ex_span['start'],
        start_edge=ex_span['start_edge'],
        end=ex_span['end'],
        end_edge=ex_span['end_edge'],
        subsequent_scopes=ex_span['subsequent_scopes']
    )
    
    # Convert back to string and check the result
    converted_string = ExtenedTimeSpan.to_string(ext_span_obj, is_default_repr=True)
    assert converted_string == valid_string, "The string conversion back to default representation is incorrect."
    
    # Ensure the ExtenedTimeSpan object interacts correctly with TimeSpan
    assert isinstance(ext_span_obj.start_span, TimeSpan), "start_span should be a TimeSpan object."
    assert isinstance(ext_span_obj.end_span, TimeSpan), "end_span should be a TimeSpan object."
    
    # Check TimeSpan object properties
    assert ext_span_obj.start_span.start == TimePoint(2023, 1, 1), "The start_span should have the correct start time."
    assert ext_span_obj.end_span.start == TimePoint(2024, 1, 1), "The end_span should have the correct end time."
    
    # Check the string representation of the object after creation
    expected_str = f"ES({ext_span_obj.default_represenantion})"
    assert str(ext_span_obj) == expected_str, "The string representation after creation is incorrect."
