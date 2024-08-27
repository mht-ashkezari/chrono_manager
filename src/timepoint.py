from __future__ import annotations


from .configs import (
    START_YEAR,
    END_YEAR,
    YEARS_WITH_53_WEEKS,
    START_SCOPE_ELEMENTS_GRE,
    START_SCOPE_ELEMENTS_ISO,
    END_SCOPE_ELEMENTS_GRE,
    END_SCOPE_ELEMENTS_ISO,
    PointType,
)
from .utilityfuncs import (
    get_value_by_unit_from_elements,
    leap_years_between,
    sort_elements_by_sequence,
    is_ordered_elements,
    what_is_sequence,
    is_elements_leap,
    find_scope_in_ordered_elements,
    find_ordered_elements_over_under_units,
    # complete_ordered_elements,
    compare_two_ordered_comparable_elements,
    add_element_to_ordered_elements,
    units_vlaues_to_ordered_elements,
    get_elements_sequence,
)
from .timeelement import TimeElement

from typing import Dict, List, Tuple, Union, Optional


class TimePointError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class TimePointCreationError(TimePointError):
    def __init__(self, message: str) -> None:
        self.message = f"Error creating TimePoint instance: {message}"
        super().__init__(self.message)


class TimePointArgumentError(TimePointError):
    def __init__(self, argument) -> None:
        self.message = f"Invalid argument: {argument}"
        super().__init__(self.message)


class TimePointNotComparableError(TimePointError):
    def __init__(self, first_timepoint, second_timepoint) -> None:

        self.message = "TimePoint instances are not comparable:"
        self.message += f" {first_timepoint}, {second_timepoint}"

        super().__init__(self.message)


class TimePointAttributeSetError(TimePointError):
    def __init__(self, attribute, value) -> None:
        self.message = f"Error setting attribute '{attribute}' with value '{value}'"
        super().__init__(self.message)


class TimePointNotSpanError(TimePointError):
    def __init__(self, point1, point2) -> None:
        self.message = f"there is no span between {point1} and {point2}"
        super().__init__(self.message)


class TimePointOccurrenceError(TimePointError):
    def __init__(self, message) -> None:
        self.message = f"Error in calculating occurrences: {message}"
        super().__init__(self.message)


class TimePoint:
    def __init__(self, telements: Union[List[TimeElement], str]) -> None:

        elements: List[TimeElement] = []
        if isinstance(telements, str):
            elems, _, unmatched = TimeElement.parse_time_string_to_elements(telements)
            if not elems:
                raise TimePointArgumentError("argument(str) has no valid elements")
            if unmatched:
                raise TimePointArgumentError(
                    f" argument(str) has unmatched substr:{unmatched}"
                )
            elements = elems
        else:
            elements = telements
        sorted_elements, missings = sort_elements_by_sequence(elements)
        if missings:
            raise TimePointArgumentError(f"argument has missing units:{missings}")
        if not sorted_elements or sorted_elements is None:
            raise TimePointArgumentError("argument has no valid elements")
        else:
            try:
                filtered_elements = [
                    el for el in sorted_elements if isinstance(el, TimeElement)
                ]
                is_ordered_elements(filtered_elements)
            except ValueError as e:
                raise TimePointCreationError(
                    f"Error in creating TimePoint instance: {e}"
                )
            else:
                self._time_elements = filtered_elements
                self._is_iso = (
                    True if what_is_sequence(self._time_elements) == "iso" else False
                )
                self._is_leap = is_elements_leap(self._time_elements)
                self._scope = find_scope_in_ordered_elements(self._time_elements)
                self._over_units = find_ordered_elements_over_under_units(
                    self._time_elements
                )["O"]
                self._under_units = find_ordered_elements_over_under_units(
                    self._time_elements
                )["U"]
                self._over_join_units = self._time_elements[0].over_join_units
                self._under_join_units = self._time_elements[-1].under_join_units
                self._point_type = PointType.START

                self._year = get_value_by_unit_from_elements("YR", self._time_elements)[
                    0
                ]
                self._month = get_value_by_unit_from_elements(
                    "MH", self._time_elements
                )[0]
                self._week = get_value_by_unit_from_elements("WK", self._time_elements)[
                    1
                ]
                self._weekday = get_value_by_unit_from_elements(
                    "WY", self._time_elements
                )[0]
                self._day = get_value_by_unit_from_elements("DY", self._time_elements)[
                    0
                ]
                self._hour = get_value_by_unit_from_elements("HR", self._time_elements)[
                    0
                ]
                self._minute = get_value_by_unit_from_elements(
                    "ME", self._time_elements
                )[0]
                self._second = get_value_by_unit_from_elements(
                    "SD", self._time_elements
                )[0]

    def __str__(self) -> str:
        return self.default_representation

    def __repr__(self) -> str:
        return f"TimePoint({self.default_representation})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TimePoint):
            return len(self.time_elements) == len(other.time_elements) and all(
                self.time_elements[i] == other.time_elements[i]
                for i in range(len(self.time_elements))
            )
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.default_representation)

    def _get_unit_values(self, unit: str) -> Optional[int]:
        for element in self._time_elements:
            if element.element_unit == unit:
                return element.element_value
        else:
            return None

    @staticmethod
    def create_timepoints_from_range(
        range_values: List[List[int]], units: List[str]
    ) -> List[TimePoint]:
        def recursive_create(dim, current_elements):
            if dim == len(range_values):
                # All dimensions have been processed, create a TimePoint
                return [TimePoint(current_elements)]

            timepoints = []
            for value in range_values[dim]:
                # Create a TimeElement for the current dimension
                time_element = TimeElement(units[dim], value)
                # Recurse to the next dimension
                new_elements = current_elements + [time_element]
                timepoints.extend(recursive_create(dim + 1, new_elements))

            return timepoints

            # Start the recursion with the first dimension

        return recursive_create(0, [])

    @staticmethod
    def is_between_points(
        point: TimePoint, start: TimePoint, end: TimePoint
    ) -> Union[int | Dict[int, int]]:
        """
        Determines if a given point is between two other points.

        Args:
            point (TimePoint): The point to check.
            start (TimePoint): The starting point.
            end (TimePoint): The ending point.

        Returns:
            Union[int | Dict[int, int]]: An indicator value or a dictionary of
                                        indicator values.
                - If the point is between the start and end, returns 0.
                - If the point is before the start, returns -1.
                - If the point is after the end, returns 1.
                - If the start and end points are not comparable, raises
                    TimePointNotComparableError.

        Raises:
            TimePointNotComparableError: If the start and end points are not comparable.

        """

        if start.scope != end.scope:
            raise TimePointNotComparableError(start, end)

        start_points = start.filled_timepoint_on_type
        end_points = end.filled_timepoint_on_type
        point_points = point.filled_timepoint_on_type
        try:
            comp_result = compare_two_ordered_comparable_elements(
                end_points.time_elements, start_points.time_elements
            )
        except ValueError as e:
            raise TimePointNotComparableError(start, end) from e
        else:
            if isinstance(comp_result, int):
                indicator: int
                if comp_result == 0:
                    raise TimePointNotSpanError(start_points, end_points)
                elif comp_result == 1:
                    # Check if the point is after the start and before the end
                    try:
                        comp_with_start = compare_two_ordered_comparable_elements(
                            point_points.time_elements, start_points.time_elements
                        )
                        comp_with_end = compare_two_ordered_comparable_elements(
                            end_points.time_elements, point_points.time_elements
                        )
                    except ValueError as e:
                        raise TimePointNotComparableError(start, end) from e
                    else:
                        if (
                            comp_with_start == 1 and comp_with_end == 1
                        ):  # point is between start and end
                            indicator = 0
                        if comp_with_start == -1:  # point is before start
                            indicator = -1
                        if comp_with_end == -1:  # point is after end
                            indicator = 1
                elif comp_result == -1:
                    indicator = 1
                else:
                    raise TimePointNotComparableError(start, end)
                return indicator
            elif isinstance(comp_result, dict):
                result: Dict[int, int] = {}
                # Get the years to compare
                year_to_compare = comp_result["greater"]
                for year in year_to_compare:
                    # Add each year to start, end, and point
                    start_elems = add_element_to_ordered_elements(
                        TimeElement("YR", year), start_points.time_elements
                    )
                    end_elems = add_element_to_ordered_elements(
                        TimeElement("YR", year), end_points.time_elements
                    )
                    point_elems = add_element_to_ordered_elements(
                        TimeElement("YR", year), point_points.time_elements
                    )
                    # Compare the point with the start and end for each year
                    try:
                        comp_with_start = compare_two_ordered_comparable_elements(
                            point_elems, start_elems
                        )
                        comp_with_end = compare_two_ordered_comparable_elements(
                            end_elems, point_elems
                        )
                    except ValueError as e:
                        raise TimePointNotComparableError(start, end) from e
                    else:
                        if (
                            comp_with_start == 1 and comp_with_end == 1
                        ):  # point is between start and end
                            result[year] = 0
                        if comp_with_start == -1:  # point is before start
                            result[year] = -1
                        if comp_with_end == -1:  # point is after end
                            result[year] = 1
                return result

    @staticmethod
    def compare_points(
        point1: TimePoint, point2: TimePoint
    ) -> int | Dict[str, List[int]]:
        """
        Compare two TimePoint objects and return the result.

        Args:
            point1 (TimePoint): The first TimePoint object to compare.
            point2 (TimePoint): The second TimePoint object to compare.

        Returns:
            int | Dict[str, List[int]]: The result of the comparison. If the TimePoint
                                        objects are comparable, an integer value is
                                        returned. If they are not comparable, a
                                        dictionary with error information is returned.

        Raises:
            TimePointNotComparableError: If the TimePoint objects have different scopes
                                        and are not comparable
        """

        if point1.scope != point2.scope:
            raise TimePointNotComparableError(point1, point2)
        try:
            result = compare_two_ordered_comparable_elements(
                point1.time_elements, point2.time_elements
            )
        except ValueError as e:
            raise TimePointNotComparableError(point1, point2) from e
        else:
            return result

    @staticmethod
    def _next_points_in_over_range(
        point: TimePoint, overs_starts: List[int], overs_ends: List[int]
    ) -> List[List[int]]:
        """
        Generate the next points in the over range.

        Args:
            point (TimePoint): The current time point.
            overs_starts (List[int]): The list of start values for each over.
            overs_ends (List[int]): The list of end values for each over.

        Returns:
            List[List[int]]: The list of next points in the over range.
        """

        overs_length = min(len(overs_starts), len(overs_ends))
        over_units = point.over_units[-overs_length:]
        has_month: bool = "MH" in over_units

        def create_ranges(
            dim: int,
            starts: List[int],
            ends: List[int],
            current_month: int,
            is_first: bool,
            is_last: bool,
        ) -> List:
            if dim == len(over_units):  # Base case: we've added all dimensions
                return []

            # Determine the current range based on whether this is
            # the first or last element in the previous dimension
            if over_units[dim] == "YR":
                current_range = list(range(starts[dim], ends[dim] + 1))
            elif over_units[dim] == "DY":
                # Assign the month value based on has_month
                month = current_month if has_month else None

                if is_first:
                    current_range = TimeElement.unit_values_to_end_scope(
                        "DY", starts[dim], month
                    )[starts[dim] - 1 :]
                elif is_last:
                    current_range = TimeElement.unit_values_to_end_scope("DY", 1, month)
                else:
                    current_range = TimeElement.unit_values_to_end_scope(
                        "DY", ends[dim], month
                    )
            else:
                if is_first:
                    current_range = list(
                        TimeElement.unit_values_to_end_scope("MH", 1, None)[
                            starts[dim] - 1 :
                        ]
                    )
                elif is_last:
                    current_range = TimeElement.unit_values_to_end_scope("MH", 1, None)
                else:
                    current_range = TimeElement.unit_values_to_end_scope(
                        "MH", ends[dim], None
                    )

            # Create the next dimension based on the current range
            next_dimension = [
                create_ranges(
                    dim + 1,
                    starts,
                    ends,
                    current_month=i + 1 if over_units[dim] == "MH" else current_month,
                    is_first=(i == 0),
                    is_last=(i == len(current_range) - 1),
                )
                for i in range(len(current_range))
            ]

            # Combine the current range with the next dimension
            if not next_dimension:
                return current_range
            return [[r] + n for r, n in zip(current_range, next_dimension)]

        # Generate the multi-dimensional range list
        result = create_ranges(
            0, overs_starts, overs_ends, current_month=1, is_first=True, is_last=True
        )
        return result

    @staticmethod
    def _create_timepoints_from_range(
        range_values: List[List[int]], units: List[str]
    ) -> List[TimePoint]:
        """
        Create a list of TimePoint objects based on the given range values and units.
        Args:
            range_values (List[List[int]]): A list of lists containing the range values
                                            for each dimension.
            units (List[str]): A list of units corresponding to each dimension.
        Returns:
            List[TimePoint]: A list of TimePoint objects created from the range values.
        """

        def recursive_create(dim, current_elements):
            if dim == len(range_values):
                # All dimensions have been processed, create a TimePoint
                return [TimePoint(current_elements)]

            timepoints = []
            for value in range_values[dim]:
                # Create a TimeElement for the current dimension
                time_element = TimeElement(units[dim], value)
                # Recurse to the next dimension
                new_elements = current_elements + [time_element]
                timepoints.extend(recursive_create(dim + 1, new_elements))

            return timepoints

            # Start the recursion with the first dimension

        return recursive_create(0, [])

    @staticmethod
    def occurrences_in_period(
        point: TimePoint, start: TimePoint, end: TimePoint
    ) -> Optional[List[TimePoint]]:
        """
        Calculate the occurrences of a given time point within a specified period.

        Args:
            point (TimePoint): The time point to check for occurrences.
            start (TimePoint): The start of the period.
            end (TimePoint): The end of the period.

        Returns:
            Optional[List[TimePoint]]: A list of time points that occur within the
                                        specified period.

        Raises:
            TimePointOccurrenceError: If there are no overlapping units in the start or
                                    end time points.
            TimePointOccurrenceError: If there are not enough units in the start or end
                                    time points.
            TimePointOccurrenceError: If the start time point is greater than or equal
                                    to the end time point.

        """

        over_units_in_start = [unit for unit in start.units if unit in point.over_units]
        over_units_in_end = [unit for unit in end.units if unit in point.over_units]
        if not over_units_in_start or not over_units_in_end:
            raise TimePointOccurrenceError(" no over units in start or end")
        if not (1 < len(over_units_in_start) <= len(point.over_units)) or not (
            1 < len(over_units_in_end) <= len(point.over_units)
        ):
            raise TimePointOccurrenceError("no sufficient units in start or end")
        overs_length = min(len(over_units_in_start), len(over_units_in_end))
        over_units = point.over_units[-overs_length:]

        for i in range(overs_length):
            if start.time_elements[i] >= end.time_elements[i]:
                raise TimePointOccurrenceError(
                    "overs_starts must be less than overs_ends"
                )
        starts = start.values[-overs_length:]
        ends = end.values[-overs_length:]
        ranges = TimePoint._next_points_in_over_range(point, starts, ends)
        return TimePoint._create_timepoints_from_range(ranges, over_units)

    @property
    def end_point_in_scope(self):
        index = self.sequence_units.index(self._scope)
        return (
            TimePoint(END_SCOPE_ELEMENTS_ISO[index:])
            if self.sequence_name == "iso"
            else TimePoint(END_SCOPE_ELEMENTS_GRE[index:])
        )

    @property
    def start_point_in_scope(self):
        index = self.sequence_units.index(self._scope)
        return (
            TimePoint(START_SCOPE_ELEMENTS_ISO[index:])
            if self.sequence_name == "iso"
            else TimePoint(START_SCOPE_ELEMENTS_GRE[index:])
        )

    @property
    def point_type(self) -> PointType:
        return self._point_type

    @point_type.setter
    def point_type(self, value: PointType) -> None:
        self._point_type = value

    @property
    def values(self) -> list[int]:
        return [el.element_value for el in self._time_elements]

    @property
    def units_values(
        self,
    ) -> Dict[str, int]:
        return {el.element_unit: el.element_value for el in self._time_elements}

    @property
    def units(self) -> list[str]:
        return [el.element_unit for el in self._time_elements]

    @property
    def sequence_units(self) -> Tuple[str]:

        return get_elements_sequence(self._time_elements)  # type: ignore

    @property
    def sequence_name(self) -> str:
        sequence_name = what_is_sequence(self._time_elements)
        assert sequence_name is not None  # a TimeElement object has a valid sequence
        return sequence_name

    @property
    def filled_timepoint_on_type(self) -> TimePoint:
        values = [val for val in self.filled_on_type if isinstance(val, int)]
        time_elms = units_vlaues_to_ordered_elements(*values)
        return TimePoint(time_elms)

    @property
    def available_years(self) -> Optional[list[int]]:
        available_years = None
        if self._is_iso and self._week == 53:
            available_years = list(YEARS_WITH_53_WEEKS)
        elif self._is_leap:
            available_years = leap_years_between(START_YEAR, END_YEAR)
        return available_years

    @property
    def start_filled(self) -> list[Union[str, int]]:
        start_array = [1, 1, 1, 0, 0, 0]
        filled: List[Union[str, int]] = []
        filled.extend(self._over_units)
        filled.extend([el.element_value for el in self._time_elements])
        filled.extend(start_array[len(filled) :])
        return filled

    @property
    def end_filled(self) -> list[Union[str, int]]:
        # if a point has only a year element, the point is gerogrian so the first under
        # unit is month if the has a week element, the point is iso so the first under
        # unit is weekday
        end_array = [1, 12, 1, 23, 59, 59]
        filled: List[Union[str, int]] = []
        filled.extend(self._over_units)
        filled.extend([el.element_value for el in self._time_elements])
        filled.extend(end_array[len(filled) :])
        return filled

    @property
    def start_point(self) -> TimePoint:
        vals = [v if isinstance(v, int) else None for v in self.start_filled]
        return TimePoint(units_vlaues_to_ordered_elements(*vals))

    @property
    def end_point(self) -> TimePoint:
        vals = [v if isinstance(v, int) else None for v in self.end_filled]
        return TimePoint(units_vlaues_to_ordered_elements(*vals))

    @property
    def filled_on_type(self) -> list[Union[str, int]]:
        return (
            self.start_filled if self.point_type == PointType.START else self.end_filled
        )

    @property
    def default_representation(self) -> str:
        return "".join([el.default_representation for el in self._time_elements])

    @property
    def alternative_representation(self) -> str:
        return "".join([el.alternative_representation for el in self._time_elements])

    @property
    def time_elements(self) -> list[TimeElement]:
        return self._time_elements

    @property
    def is_iso(self) -> bool:
        return self._is_iso

    @property
    def is_leap(self) -> bool:
        return self._is_leap

    @property
    def scope(self) -> Optional[str]:
        return self._scope

    @property
    def over_units(self) -> list[str]:
        return self._over_units

    @property
    def under_units(self) -> list[str]:
        return self._under_units

    @property
    def year(self) -> Optional[int]:
        return self._year

    @property
    def month(self) -> Optional[int]:
        return self._month

    @property
    def week(self) -> Optional[int]:
        return self._week

    @property
    def day(self) -> Optional[int]:
        return self._day

    @property
    def weekday(self) -> Optional[int]:
        return self._weekday

    @property
    def hour(self) -> Optional[int]:
        return self._hour

    @property
    def minute(self) -> Optional[int]:
        return self._minute

    @property
    def second(self) -> Optional[int]:
        return self._second
