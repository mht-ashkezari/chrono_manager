from __future__ import annotations
from .constants import (
    EdgeType,
    SpanContain,
    SpanType,
)
from .timepoint import (
    TimePoint,
    TimePointArgumentError,
    TimePointNotComparableError,
    TimePointOccurrenceError,
)

from typing import Dict, List, Optional, Tuple, Union

from .utilityfuncs import find_intersection

from .configs import CombinedSequnce


class TimeSpanError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TimeSpanCreateArgumentError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TimeSpanOccurrenceError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TimeSpanContainmentError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TimeSpanStringError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TimeSpan:
    def __init__(
        self,
        start: Union[TimePoint, str],
        start_edge: Optional[EdgeType] = None,
        end: Optional[TimePoint] = None,
        end_edge: Optional[EdgeType] = None,
        span_type: SpanType = SpanType.BETWEEN,
    ):
        """
        Initialize a TimeSpan object.

        Args:
            start (Union[TimePoint, str]): The start time point or a string representation of the time span.
            start_edge (Optional[EdgeType]): The edge type for the start time point.
            end (Optional[TimePoint]): The end time point.
            end_edge (Optional[EdgeType]): The edge type for the end time point.
            span_type (SpanType): The type of time span.

        Raises:
            TimeSpanCreateArgumentError: If there is an error in creating the TimeSpan object.

        Notes:

            - SpanType sepcifies the type of the time span. It can be one of the following:
                - SpanType.BETWEEN: The time span is between two time points.
                - SpanType.AFTER: The time span is after a time point.
                - SpanType.BEFORE: The time span is before a time point.
            _EdgeType specifies the edge type of the time point. It can be one of the following:
                - EdgeType.START: The time point under units are set to the values of the start.
                    for exapmple for point consist on month and day with the EdgeType.START, its
                    under units (hour,minute,second) are set to 0.
                - EdgeType.END: The time point under units are set to the values of the end.
                    for exapmple for point consist on month and day with the EdgeType.END, its
                    under units (hour,minute,second) are set to 23:59:39.
            - If `start` is a string, it is parsed to create the TimeSpan object.
            - If `start` is a TimePoint object, the TimeSpan object is created using the provided arguments.

        """

        func_name = TimeSpan.__init__.__name__
        if isinstance(start, str):
            try:
                prsed_arguments = TimeSpan.parse_time_span_string(start)

            except TimeSpanStringError as e:
                raise TimeSpanCreateArgumentError(f"{func_name}: {e}") from e
            else:
                start = prsed_arguments["start"]
                start_edge = prsed_arguments["start_edge"]
                end = prsed_arguments["end"]
                end_edge = prsed_arguments["end_edge"]
                span_type = prsed_arguments["span_type"]

        self._init_start = start
        self._init_end = end
        if start is None:
            raise TimeSpanCreateArgumentError("start cannot be None")
        elif end is None:
            self._sequence_combination = (
                CombinedSequnce.ISO if start.is_iso else CombinedSequnce.GRE
            )
            self._is_leap = start.is_leap
            self._available_years = start.available_years
            self._type = span_type
            self._scope = start.scope

            if span_type == SpanType.BETWEEN:
                if start_edge == EdgeType.END:
                    raise TimeSpanCreateArgumentError(
                        "start_edge cannot be 'EdgeType.END' when span_type is 'Sapn.Type.BETWEEN'"
                    )
                self._start = start.start_point
                self._end = start.end_point
                self._start_edge = EdgeType.START
                self._end_edge = EdgeType.END
            elif span_type == SpanType.AFTER:
                self._start = (
                    start.start_point
                    if start_edge == EdgeType.START
                    else start.end_point
                )
                self._end = start.end_point_in_scope
                self._start_edge = start_edge
                self._end_edge = EdgeType.END
            elif span_type == SpanType.BEFORE:
                self._start = start.start_point_in_scope
                self._end = (
                    start.start_point
                    if start_edge == EdgeType.START
                    else start.end_point
                )
                self._start_edge = EdgeType.START
                self._end_edge = start_edge
        else:
            if start.scope != end.scope:
                raise TimeSpanCreateArgumentError(
                    "start and end must have the same scope"
                )

            self._sequence_combination = (
                CombinedSequnce.ISO_GRE
                if start.is_iso ^ end.is_iso
                else (
                    CombinedSequnce.ISO
                    if start.is_iso and end.is_iso
                    else CombinedSequnce.GRE
                )
            )
            self._is_leap = start.is_leap or end.is_leap
            self._type = SpanType.BETWEEN
            self._start_edge = start_edge or EdgeType.START
            self._end_edge = end_edge or EdgeType.END
            self._scope = start.scope
            self._available_years = find_intersection(
                start.available_years, end.available_years
            )

            try:
                result = TimePoint.compare_points(end, start)
            except TimePointNotComparableError as e:
                raise TimeSpanCreateArgumentError(e) from e

            if result == 0:
                raise TimeSpanCreateArgumentError(
                    "start and end are equal; there is no span"
                )
            elif result == -1:
                raise TimeSpanCreateArgumentError("start is greater than end")
            elif result == -2:
                raise TimeSpanCreateArgumentError("start and end are not comparable")
            elif result == 1 or (isinstance(result, dict) and result):
                self._available_years = (
                    result.get("greater") if isinstance(result, dict) else None
                )
                self._start = (
                    start.start_point
                    if self._start_edge == EdgeType.START
                    else start.end_point
                )
                self._end = (
                    end.start_point
                    if self._end_edge == EdgeType.START
                    else end.end_point
                )
            else:
                raise TimeSpanCreateArgumentError(
                    "No span exists between start and end"
                )

    def __str__(self) -> str:
        return f"S({self.default_represenantion})"

    def __repr__(self) -> str:
        return f"TimeSpan('{self.default_represenantion}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeSpan):
            return NotImplemented
        return (
            self.start == other.start
            and self.end == other.end
            and self.start_edge == other.start_edge
            and self.end_edge == other.end_edge
            and self.type == other.type
        )

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, TimeSpan):
            return NotImplemented
        return (
            self.start != other.start
            or self.end != other.end
            or self.start_edge != other.start_edge
            or self.end_edge != other.end_edge
            or self.type != other.type
        )
    
    def __hash__(self) -> int:
        return hash(
            (
                self.start,
                self.end,
                self.start_edge,
                self.end_edge,
                self.type,
            )
        )
    @staticmethod
    def parse_time_span_string(span_str: str) -> dict:
        """
        Parses a time span string and returns a dictionary representing the time span.

        Args:
            span_str (str): The time span string to parse.

        Returns:
            dict: A dictionary representing the parsed time span with the following keys:
                - "start" (TimePoint): The start time point of the time span.
                - "start_edge" (EdgeType): The edge type of the start time point.
                - "end" (TimePoint): The end time point of the time span.
                - "end_edge" (EdgeType): The edge type of the end time point.
                - "span_type" (SpanType): The type of the time span.

        Raises:
            TimeSpanStringError: If the time span string is empty or whitespace, or if it is not formatted correctly.

        """
        func_name = TimeSpan.parse_time_span_string.__name__

        if not span_str or span_str.isspace():
            raise TimeSpanStringError(
                f"{func_name}: TimeSpan string cannot be empty or whitespace"
            )

        # Helper function to create TimePoint safely
        def create_timepoint(tp_str: str) -> TimePoint:
            try:
                return TimePoint(tp_str)
            except TimePointArgumentError as e:
                raise TimeSpanStringError(
                    f"{func_name}: TimePoint creation failed: {e}"
                ) from e

        # Handle single timepoint cases (without '_')
        if "_" not in span_str:
            if span_str.startswith("@") and span_str.endswith("@"):
                start_timepoint = create_timepoint(span_str[1:-1])
                return {
                    "start": start_timepoint,
                    "start_edge": EdgeType.START,
                    "end": None,
                    "end_edge": None,
                    "span_type": SpanType.BETWEEN,
                }
            else:
                raise TimeSpanStringError(
                    f"{func_name}: TimeSpan string must start and end with '@'"
                )

        # Handle cases with start and end components
        start_str, end_str = (part.strip() for part in span_str.split("_", 1))

        if not start_str and not end_str:
            raise TimeSpanStringError(
                f"{func_name}: Invalid TimeSpan string with no components"
            )

        span_type = (
            SpanType.BETWEEN
            if start_str and end_str
            else SpanType.BEFORE if start_str else SpanType.AFTER
        )

        def determine_edge_type(tp_str: str, is_start: bool) -> Tuple[str, EdgeType]:
            if tp_str.startswith("@"):
                return tp_str[1:], EdgeType.START
            elif tp_str.endswith("@"):
                return tp_str[:-1], EdgeType.END
            else:
                raise TimeSpanStringError(
                    f"{func_name}: Missing '@' in the {'start' if is_start else 'end'} component"
                )

        if span_type == SpanType.BETWEEN:
            start_str, start_edge = determine_edge_type(start_str, True)
            end_str, end_edge = determine_edge_type(end_str, False)
        elif span_type == SpanType.BEFORE:
            start_str, start_edge = determine_edge_type(start_str, True)
            end_edge, end_str = None, None
        elif span_type == SpanType.AFTER:
            start_str, start_edge = determine_edge_type(end_str, False)
            end_str, end_edge = None, None

        start_timepoint = create_timepoint(start_str) if start_str else None
        end_timepoint = create_timepoint(end_str) if end_str else None

        return {
            "start": start_timepoint,
            "start_edge": start_edge,
            "end": end_timepoint,
            "end_edge": end_edge,
            "span_type": span_type,
        }

    @property
    def start(self) -> TimePoint:
        """
        Returns the start point of the timespan.

        :return: The start point of the timespan.
        :rtype: TimePoint
        """
        return self._start

    @property
    def end(self) -> TimePoint:
        """
        Returns the end time of the timespan.

        :return: The end time of the timespan.
        :rtype: TimePoint
        """
        return self._end

    @property
    def start_edge(self) -> EdgeType:
        """
        Returns the edge of the timespan's start point.

        :return: The edge of the timespan's start point.
        :rtype: EdgeType
        """
        return self._start_edge

    @property
    def end_edge(self) -> EdgeType:
        """
        Returns the edge of the timespan's end point.

        :return: The edge of the timespan's end point.
        :rtype: EdgeType
        """
        return self._end_edge

    @property
    def init_start(self) -> TimePoint:
        """
        Returns the initial value of start point passed as an argument.

        :return: The initial value of start point passed as an argument.
        :rtype: TimePoint
        """
        return self._init_start

    @property
    def init_end(self) -> Optional[TimePoint]:
        """
        Returns the initial value of end point passed as an argument.

        :return: The initial value of end point passed as an argument.
        :rtype: Optional[TimePoint]
        """
        return self._init_end

    @property
    def type(self) -> SpanType:
        """
        Returns the type of the timespan.

        :return: The type of the timespan.
        :rtype: SpanType
        """
        return self._type

    @property
    def sequence_combination(self) -> CombinedSequnce:
        """
        Returns the combined sequence of the timespan.

        :return: The combined sequence of the timespan.
        :rtype: CombinedSequnce
        """
        return self._sequence_combination

    @property
    def is_leap(self) -> bool:
        """
        Returns a boolean value indicating whether the timespan is in a leap year.

        :return: True if the timespan is in a leap year, False otherwise.
        :rtype: bool
        """
        return self._is_leap

    @property
    def scope(self) -> Optional[str]:
        """
        Returns the unit scope of the timespan.

        :return: The scope of the timespan.
        :rtype: Optional[str]
        """
        return self._scope

    @property
    def available_years(self) -> Optional[List[int]]:
        """
        Returns the list of the years the timespan is available in.
        None if the timespan is available in all years.

        :return: The list of the years the timespan is available in.
        :rtype: Optional[List[int]]
        """
        return self._available_years

    @property
    def default_represenantion(self) -> str:
        """
        Returns the default representation of the timespan.

        :return: The default representation of the timespan.
        :rtype: str
        """
        return self.time_span_to_span_string(self, True)

    @property
    def alternative_represenantion(self) -> str:
        """
        Returns the alternative representation of the timespan.

        :return: The alternative representation of the timespan.
        :rtype: str
        """
        return self.time_span_to_span_string(self, False)

    @staticmethod
    def occurrences_in_period(
        time_span: TimeSpan, period_start: TimePoint, period_end: TimePoint
    ) -> Optional[List[TimeSpan]]:
        """
        Calculate the occurrences of a given time span within a specified period.

        Args:
            time_span (TimeSpan): The time span to calculate occurrences for.
            period_start (TimePoint): The start of the period.
            period_end (TimePoint): The end of the period.

        Returns:
            Optional[List[TimeSpan]]: A list of time spans representing the occurrences within the period.
            Returns None if there are no occurrences.

        Raises:
            TimeSpanOccurrenceError: If the time_span is not of type BETWEEN.
            TimePointOccurrenceError: If there is an error calculating the occurrences of the start or end time points.

        """

        if time_span.type != SpanType.BETWEEN:
            raise TimeSpanOccurrenceError("time_span must be of type BETWEEN")

        occurrences: List[TimeSpan] = []
        span_start = time_span.start
        span_end = time_span.end
        start_edge = time_span.start_edge
        end_edge = time_span.end_edge

        try:
            start_occurrences = TimePoint.occurrences_in_period(
                span_start, period_start, period_end
            )
            end_occurrences = TimePoint.occurrences_in_period(
                span_end, period_start, period_end
            )
        except TimePointOccurrenceError as e:
            raise TimeSpanOccurrenceError(e)

        if not start_occurrences or not end_occurrences:
            return None

        start_occurrences_len = len(start_occurrences)
        end_occurrences_len = len(end_occurrences)

        if start_occurrences_len < 1 or end_occurrences_len < 1:
            return []

        if start_occurrences_len < end_occurrences_len:
            start_occurrences = start_occurrences[1:]
        elif start_occurrences_len > end_occurrences_len:
            end_occurrences = end_occurrences[:-1]

        occurrences_pairs = zip(start_occurrences, end_occurrences)
        occurrences = [
            TimeSpan(
                start_occurrence,
                start_edge,
                end_occurrence,
                end_edge,
                SpanType.BETWEEN,
            )
            for start_occurrence, end_occurrence in occurrences_pairs
        ]

        return occurrences

    @staticmethod
    def occurrences_in_sapn(
        contained_span: TimeSpan, container_span: TimeSpan
    ) -> Optional[List[TimeSpan]]:
        """
        Calculates the occurrences of a contained time span within a container time span.

        Args:
            contained_span (TimeSpan): The time span to be checked for occurrences.
            container_span (TimeSpan): The time span within which occurrences are checked.

        Returns:
            Optional[List[TimeSpan]]: A list of time spans representing the occurrences of the contained span within the container span.
                                        Returns None if no occurrences are found.

        Raises:
            TimeSpanOccurrenceError: If an error occurs while calculating the occurrences.

        """

        try:
            return TimeSpan.occurrences_in_period(
                contained_span, container_span.start, container_span.end
            )
        except TimeSpanOccurrenceError as e:
            raise TimeSpanOccurrenceError(e) from e

    @staticmethod
    def is_contained_in_preiod(time_span: TimeSpan, start: TimePoint, end: TimePoint):
        def check_contained(start_con: int, end_con: int) -> SpanContain:
            if start_con == 1 and end_con == 1:
                return SpanContain.AHEAD
            elif start_con == 0 and end_con == 0:
                return SpanContain.INSIDE
            elif start_con == -1 and end_con == -1:
                return SpanContain.BEHIND
            elif start_con == 0 and end_con == 1:
                return SpanContain.END_OVERLAPPED
            elif start_con == -1 and end_con == 0:
                return SpanContain.START_OVERLAPPED
            else:
                return SpanContain.ERROR

        try:
            temp_dict: Dict[int, SpanContain] = {}
            start_contained = TimePoint.is_between_points(time_span.start, start, end)
            end_contained = TimePoint.is_between_points(time_span.end, start, end)
            if isinstance(start_contained, int) and isinstance(end_contained, int):
                return check_contained(start_contained, end_contained)
            elif isinstance(start_contained, Dict) and isinstance(end_contained, int):
                temp_dict = {
                    y: check_contained(start_contained[y], end_contained)
                    for y in start_contained.keys()
                }

            elif isinstance(start_contained, int) and isinstance(end_contained, Dict):
                temp_dict = {
                    y: check_contained(end_contained[y], start_contained)
                    for y in end_contained.keys()
                }

            elif isinstance(start_contained, Dict) and isinstance(end_contained, Dict):
                temp_dict = {
                    y: check_contained(start_contained[y], end_contained[y])
                    for y in start_contained.keys()
                    if y in end_contained
                }
        except TimePointOccurrenceError as e:
            raise TimeSpanOccurrenceError(e) from e
        else:
            return temp_dict

    @staticmethod
    def is_contained_in_span(
        contained_span: TimeSpan, container_span: TimeSpan
    ) -> Optional[SpanContain]:
        """
        Determines if the `contained_span` is fully contained
                        within the `container_span`.

        Args:
            contained_span (TimeSpan): The TimeSpan to check if it is contained within
                                        the container_span.
            container_span (TimeSpan): The TimeSpan that potentially contains the
                                        contained_span.

        Returns:
            Optional[SpanContain]: The result of the containment check. It can be one
                                    of the following:
                - SpanContain.CONTAINED: If the `contained_span` is fully contained
                                            within the `container_span`.
                - SpanContain.STARTS_BEFORE: If the `contained_span` starts before the
                                            `container_span` but ends within it.
                - SpanContain.ENDS_AFTER: If the `contained_span` starts within the
                                            `container_span` but ends after it.
                - SpanContain.NOT_CONTAINED: If the `contained_span` is not contained
                                            within the `container_span`.
        """

        try:
            return TimeSpan.is_contained_in_preiod(
                contained_span, container_span.start, container_span.end
            )
        except TimeSpanOccurrenceError as e:
            raise TimeSpanOccurrenceError(e) from e

    @staticmethod
    def time_span_to_span_string(time_span: TimeSpan, is_default_repr: bool) -> str:
        """
        Convert a TimeSpan object to a string representation.

        Args:
            time_span (TimeSpan): The TimeSpan object to convert to a string.
            is_default_repr (bool): A boolean value indicating whether to use the default representation.

        Returns:
            str: The string representation of the TimeSpan object.

        Raises:
            TimeSpanStringError: If there is an error in converting the TimeSpan object to a string.
        """

        def get_representation(start=True):
            """Helper to get the correct representation for start or end."""
            if start:

                return (
                    time_span.init_start.default_representation
                    if is_default_repr
                    else time_span.init_start.alternative_representation
                )
            else:
                return (
                    time_span.init_end.default_representation
                    if is_default_repr
                    else time_span.init_end.alternative_representation
                )

        def set_edge_marker(edge_type, init_str):
            """Helper to get the marker based on edge type and position."""
            return f"@{init_str}" if edge_type == EdgeType.START else f"{init_str}@"

        if time_span.init_end is None:
            if time_span.type == SpanType.BETWEEN:
                return f"@{get_representation(start=True)}@"
            elif time_span.type == SpanType.AFTER:
                return f"_{set_edge_marker(time_span.start_edge, get_representation(start=True))}"
            elif time_span.type == SpanType.BEFORE:
                return f"{set_edge_marker(time_span.start_edge, get_representation(start=True))}_"
        else:
            start_repr = get_representation(True)
            end_repr = get_representation(start=False)
            start_with_marker = set_edge_marker(time_span.start_edge, start_repr)
            end_with_marker = set_edge_marker(time_span.end_edge, end_repr)
            return f"{start_with_marker}_{end_with_marker}"

        raise TimeSpanStringError("Invalid TimeSpan configuration")
