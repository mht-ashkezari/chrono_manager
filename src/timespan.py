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

from typing import Dict, List, Optional

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
        start: TimePoint,
        start_edge: EdgeType,
        end: Optional[TimePoint] = None,
        end_edge: Optional[EdgeType] = None,
        span_type: SpanType = SpanType.BETWEEN,
    ):
        self._init_start = start
        self._init_end = end

        if end is None:
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
                        "start_edge cannot be 'END' when span_type is 'BETWEEN'"
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
            self._start_edge = start_edge
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
        return (
            f"start = {self._start}, start_edge ={ self._start_edge},"
            f" end = {self._end}, end_edge = {self._end_edge}, "
            f"span_type = {self._type}"
        )

    def __repr__(self) -> str:
        return f"TimeSpan({self.__str__()})"

    @property
    def start(self) -> TimePoint:
        return self._start

    @property
    def end(self) -> TimePoint:
        return self._end

    @property
    def start_edge(self) -> EdgeType:
        return self._start_edge

    @property
    def end_edge(self) -> EdgeType:
        return self._end_edge

    @property
    def init_start(self) -> TimePoint:
        return self._init_start

    @property
    def init_end(self) -> Optional[TimePoint]:
        return self._init_end

    @property
    def type(self) -> SpanType:
        return self._type

    @property
    def sequence_combination(self) -> CombinedSequnce:
        return self._sequence_combination

    @property
    def is_leap(self) -> bool:
        return self._is_leap

    @property
    def scope(self) -> Optional[str]:
        return self._scope

    @property
    def available_years(self) -> Optional[List[int]]:
        return self._available_years

    @staticmethod
    def parse_time_span_string(span_str: str) -> dict:
        func_name = TimeSpan.parse_time_span_string.__name__
        if not span_str:
            raise TimeSpanStringError(f"{func_name}: TimeSpan string cannot be empty")

        # Split the string by the underscore, identifying start and end components
        if "_" not in span_str:
            if not span_str or span_str.isspace():
                raise TimeSpanStringError(
                    f"{func_name}: TimeSpan string cannot be empty or whitespace"
                )
            if span_str.startswith("@") and span_str.endswith("@"):
                try:
                    start_timepoint = TimePoint(span_str[1:-1])
                except TimePointArgumentError as e:
                    raise TimeSpanStringError(
                        f"{func_name}:" f"TimePoint instance is not created: {e}"
                    ) from e
                else:
                    return {
                        "start": start_timepoint,
                        "start_edge": EdgeType.START,
                        "end": None,
                        "end_edge": None,
                        "span_type": SpanType.BETWEEN,
                    }
            else:
                raise TimeSpanStringError(
                    f"{func_name}: "
                    "TimeSpan string without '_' must start and end with @"
                )
        else:
            parts = span_str.split("_")

            # Determine the start and end strings, and whether they exist
            start_str = parts[0] if parts[0] else None
            end_str = parts[1] if len(parts) > 1 else None

            span_type: SpanType
            # Determine the SpanType
            if start_str and end_str and not (start_str.isspace() or end_str.isspace()):
                span_type = SpanType.BETWEEN
            elif start_str and not start_str.isspace():
                span_type = SpanType.BEFORE
            elif end_str and not end_str.isspace():
                span_type = SpanType.AFTER
            else:
                raise TimeSpanStringError(
                    f"{func_name}: TimeSpan type check: string with start :"
                    f"'{start_str}' and end '{end_str}'"
                    f" components is not valid for type ''{span_type}' "
                )
            # Determine start_edge
            start_at_sign_begin = (
                True
                if start_str and start_str.startswith("@")
                else False if start_str and start_str.endswith("@") else None
            )

            end_at_sign_begin = (
                True
                if end_str and end_str.startswith("@")
                else False if end_str and end_str.endswith("@") else None
            )
            print(
                f"start_at_sign_begin: {start_at_sign_begin}, end_at_sign_begin: {end_at_sign_begin}"
            )
            print("span_type:", span_type)
            if end_at_sign_begin is None and start_at_sign_begin is None:
                raise TimeSpanStringError(f"{func_name}: TimeSpan string must have '@'")

            if (
                span_type == SpanType.BETWEEN
                and end_at_sign_begin is not None
                and start_at_sign_begin is not None
            ):
                if start_at_sign_begin:
                    start_edge = EdgeType.START
                    start_str = start_str.lstrip("@")  # Remove the leading '@'
                else:
                    start_edge = EdgeType.END
                    start_str = start_str.rstrip("@")  # Remove the trailing '@'
                if end_at_sign_begin:
                    end_edge = EdgeType.START
                    end_str = end_str.lstrip("@")
                else:
                    end_edge = EdgeType.END
                    end_str = end_str.rstrip("@")

            elif span_type == SpanType.AFTER and end_at_sign_begin is not None:
                if end_at_sign_begin:
                    start_edge = EdgeType.START
                    start_str = end_str.lstrip("@")
                else:
                    start_edge = EdgeType.END
                    start_str = end_str.rstrip("@")

                end_str = ""
                end_edge = None

            elif span_type == SpanType.BEFORE and start_at_sign_begin is not None:

                if end_at_sign_begin:
                    start_edge = EdgeType.START
                    start_str = end_str.lstrip("@")
                else:
                    start_edge = EdgeType.END
                    start_str = end_str.rstrip("@")

                end_edge = None
                end_str = ""

            else:
                raise TimeSpanStringError(
                    f"{func_name}: TimeSpan string with start :"
                    f" '{start_str}' and end '{end_str}'"
                    f" components is not valid for type ''{span_type}' "
                )

            try:
                start_timepoint = TimePoint(start_str) if start_str else None
                end_timepoint = TimePoint(end_str) if end_str else None
            except TimePointArgumentError as e:
                raise TimeSpanStringError(
                    f"{func_name}:TimePoint instance is not created {e}"
                ) from e
            else:
                # Return the parsed arguments as a dictionary
                return {
                    "start": start_timepoint,
                    "start_edge": start_edge,
                    "end": end_timepoint,
                    "end_edge": end_edge,
                    "span_type": span_type,
                }

    @staticmethod
    def occurrences_in_period(
        time_span: TimeSpan, period_start: TimePoint, period_end: TimePoint
    ) -> Optional[List[TimeSpan]]:
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
            end_contained = TimePoint.is_between_points(time_span.end, end, start)
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
        try:
            return TimeSpan.is_contained_in_preiod(
                contained_span, container_span.start, container_span.end
            )
        except TimeSpanOccurrenceError as e:
            raise TimeSpanOccurrenceError(e) from e
