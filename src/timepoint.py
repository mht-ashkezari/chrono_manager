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
        if isinstance(telements, str):
            elements = self._parse_elements_from_string(telements)
        else:
            elements = telements

        sorted_elements, missing_units = sort_elements_by_sequence(elements)

        if missing_units:
            raise TimePointArgumentError(f"Missing units in argument: {missing_units}")

        if not sorted_elements:
            raise TimePointArgumentError("No valid elements found in the argument")

        self._initialize_time_point(sorted_elements)

    def _parse_elements_from_string(self, telements: str) -> List[TimeElement]:
        try:
            elements, _, unmatched = TimeElement.parse_time_string_to_elements(
                telements
            )
        except ValueError as e:
            raise TimePointCreationError(f"Error in creating TimePoint instance: {e}")

        if not elements:
            raise TimePointArgumentError("String argument has no valid elements")

        if unmatched:
            raise TimePointArgumentError(
                f"String argument has unmatched substring: {unmatched}"
            )

        return elements

    def _initialize_time_point(self, elements: List[TimeElement]) -> None:
        try:
            is_ordered_elements(elements)
        except ValueError as e:
            raise TimePointCreationError(f"Error in creating TimePoint instance: {e}")

        self._time_elements = elements
        self._is_iso = what_is_sequence(self._time_elements) == "iso"
        self._is_leap = is_elements_leap(self._time_elements)
        self._scope = find_scope_in_ordered_elements(self._time_elements)
        self._over_units = self._find_units("O")
        self._under_units = self._find_units("U")
        self._over_join_units = self._time_elements[0].over_join_units
        self._under_join_units = self._time_elements[-1].under_join_units
        self._point_type = PointType.START

        self._initialize_time_units()

    def _find_units(self, unit_type: str) -> List[str]:
        return find_ordered_elements_over_under_units(self._time_elements)[unit_type]

    def _initialize_time_units(self) -> None:
        self._year = self._get_unit_value("YR")
        self._month = self._get_unit_value("MH")
        self._week = self._get_unit_value("WK")
        self._weekday = self._get_unit_value("WY")
        self._day = self._get_unit_value("DY")
        self._hour = self._get_unit_value("HR")
        self._minute = self._get_unit_value("ME")
        self._second = self._get_unit_value("SD")

    def _get_unit_value(self, unit: str) -> Optional[int]:
        return get_value_by_unit_from_elements(unit, self._time_elements)[0]

    def __str__(self) -> str:
        return self.default_representation

    def __repr__(self) -> str:
        return f"TimePoint('{self.default_representation}')"

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
            print("compare: ", comp_result)
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
    def _points_occurances_in_over_range(
        point: TimePoint, overs_starts: List[int], overs_ends: List[int]
    ) -> List[TimePoint]:
        overs_length = min(len(overs_starts), len(overs_ends))
        point_over_units = point.over_units
        over_units = point_over_units[-overs_length:]
        null_over = [None] * (len(point_over_units) - overs_length)

        has_month: bool = "MH" in over_units

        def create_timepoints(
            dim: int,
            starts: List[int],
            ends: List[int],
            current_month: int,
            accumulated_values: List[int],
            is_first: bool,
            is_last: bool,
        ) -> List[TimePoint]:
            if dim == len(over_units):
                # Create a TimePoint at the deepest level of recursion
                all_values = (
                    null_over
                    + accumulated_values
                    + list(point.filled_timepoint_on_type.values)
                )

                elements = units_vlaues_to_ordered_elements(*all_values, point.is_iso)
                return [TimePoint(elements)]

            results_list = []
            month = None  # Initialize month to ensure it always has a value
            if over_units[dim] == "DY":
                month = current_month if has_month else None

            if over_units[dim] == "YR":
                current_range = list(range(starts[dim], ends[dim] + 1))
            else:
                if is_first:
                    current_range = TimeElement.unit_values_to_end_scope(
                        over_units[dim], 1, None
                    )[starts[dim] - 1 :]
                elif is_last:
                    current_range = TimeElement.unit_values_to_end_scope(
                        over_units[dim], 1, None
                    )[: ends[dim]]
                else:
                    current_range = TimeElement.unit_values_to_end_scope(
                        over_units[dim], 1, month
                    )

            for i, val in enumerate(current_range):
                new_accumulated_values = accumulated_values + [val]
                results_list.extend(
                    create_timepoints(
                        dim + 1,
                        starts,
                        ends,
                        current_month=(
                            i + 1 if over_units[dim] == "MH" else current_month
                        ),
                        accumulated_values=new_accumulated_values,
                        is_first=(i == 0),
                        is_last=(i == len(current_range) - 1),
                    )
                )

            return results_list

        result = create_timepoints(
            0,
            overs_starts,
            overs_ends,
            current_month=1,
            accumulated_values=[],
            is_first=True,
            is_last=True,
        )
        return result

    @staticmethod
    def occurrences_in_period(
        point: "TimePoint", start: "TimePoint", end: "TimePoint"
    ) -> Optional[List["TimePoint"]]:
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

        common_units = set(start.units).intersection(end.units)

        point_required_units = set(point.over_units[-2:])

        if not point_required_units.issubset(common_units):
            raise TimePointOccurrenceError(
                "Insufficient units in start or end time points."
            )

        start_point_common_count = sum(1 for unit in start.units if unit in point.units)
        end_point_common_count = sum(1 for unit in end.units if unit in point.units)

        len_start_over_point = len(start.units) - start_point_common_count
        len_end_over_point = len(end.units) - end_point_common_count

        common_over_length = min(len_start_over_point, len_end_over_point)
        start_values = start.values[
            -(len_start_over_point + common_over_length) : -(len_start_over_point - 1)
        ]
        end_values = end.values[
            -(len_end_over_point + common_over_length) : -(len_end_over_point - 1)
        ]

        for start_value, end_value in zip(start_values, end_values):
            if start_value < end_value:
                break
        else:
            raise TimePointOccurrenceError("Start values must be less than end values.")

        return TimePoint._points_occurances_in_over_range(
            point, start_values, end_values
        )

    @property
    def end_point_in_scope(self):
        if self._scope is None:
            index = 0
        else:
            index = self.sequence_units.index(self._scope)
        return (
            TimePoint(list(END_SCOPE_ELEMENTS_ISO[index:]))
            if self.sequence_name == "iso"
            else TimePoint(list(END_SCOPE_ELEMENTS_GRE[index:]))
        )

    @property
    def start_point_in_scope(self) -> TimePoint:
        if self._scope is None:
            index = 0
        else:
            index = self.sequence_units.index(self._scope)
        return (
            TimePoint(list(START_SCOPE_ELEMENTS_ISO[index:]))
            if self.sequence_name == "iso"
            else TimePoint(list(START_SCOPE_ELEMENTS_GRE[index:]))
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
        values = [val if isinstance(val, int) else None for val in self.filled_on_type]
        values.append(self.is_iso)
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
        vals.append(self.is_iso)
        return TimePoint(units_vlaues_to_ordered_elements(*vals))

    @property
    def end_point(self) -> TimePoint:
        vals = [v if isinstance(v, int) else None for v in self.end_filled]
        vals.append(self.is_iso)
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
