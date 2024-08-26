from __future__ import annotations
from constants import (
    EdgeType,
    SpanContain,
    SpanType,
)
from timepoint import TimePoint, TimePointNotComparableError, TimePointOccurrenceError

from typing import Dict, List, Optional

from utilityfuncs import find_intersection


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


class TimeSpan:
    def __init__(
        self,
        start: TimePoint,
        start_edge: EdgeType,
        end: Optional[TimePoint],
        end_edge: Optional[EdgeType],
        span_type: SpanType = SpanType.BETWEEN,
    ):
        self._init_start = start
        self._init_end = end
        if end is None:
            self._is_iso = True if start.is_iso else False
            self._is_leap = True if start.is_leap else False
            self._available_years = start.available_years
            self._type = span_type
            self._scope = start.scope
            if span_type == SpanType.BETWEEN:
                self._available_years = start.available_years
                if start_edge == EdgeType.END:
                    raise TimeSpanCreateArgumentError(
                        "start_edge could not be end if the span_type is between"
                    )
                else:
                    self._type = SpanType.BETWEEN
                    self._start = start.start_point
                    self._end = start.end_point
                    self._start_edge = EdgeType.START
                    self._end_edge = EdgeType.END
            elif span_type == SpanType.AFTER:
                if start_edge == EdgeType.START:
                    self._start = start.start_point
                    self._end = start.end_point_in_scope
                    self._start_edge = EdgeType.START
                    self._end_edge = EdgeType.END
                else:
                    self._start = start.end_point
                    self._end = start.end_point_in_scope
                    self._start_edge = EdgeType.END
                    self._end_edge = EdgeType.END
            elif span_type == SpanType.BEFORE:
                if start_edge == EdgeType.START:
                    self._start = start.start_point_in_scope
                    self._end = start.start_point
                    self._start_edge = EdgeType.START
                    self._end_edge = EdgeType.START
                else:
                    self._start = start.start_point_in_scope
                    self._end = start.end_point
                    self._start_edge = EdgeType.START
                    self._end_edge = EdgeType.END
        else:
            if start.scope != end.scope:
                raise TimeSpanCreateArgumentError(
                    "start and end must have the same scope"
                )
            self._is_iso = True if start.is_iso or end.is_iso else False
            self._is_leap = True if start.is_leap or end.is_leap else False
            self._type = SpanType.BETWEEN
            self._start_edge = start_edge
            assert end_edge is not None, "end_edge is not None"
            self._end_edge = end_edge
            self._scope = start.scope
            self._available_years = find_intersection(
                start.available_years, end.available_years
            )
            try:
                result = TimePoint.compare_points(end, start)
            except TimePointNotComparableError as e:
                raise TimeSpanCreateArgumentError(e) from e
            else:
                if result == 0:
                    raise TimeSpanCreateArgumentError(
                        "start and end are equal, there is no span"
                    )
                elif result == -1:
                    raise TimeSpanCreateArgumentError("start is greater than end")
                elif result == -2:
                    raise TimeSpanCreateArgumentError(
                        "start and end are not comparable"
                    )
                elif result == 1:
                    if self._start_edge == EdgeType.START:
                        self._start = start.start_point
                    else:
                        self._start = start.end_point
                    if self._end_edge == EdgeType.START:
                        self._end = end.start_point
                    else:
                        self._end = end.end_point

                elif isinstance(result, Dict) and result is not None:
                    greater = result.get("greater")
                    if greater is not None:
                        self._possible_years = greater
                        if self._start_edge == EdgeType.START:
                            self._start = start.start_point
                        else:
                            self._start = start.end_point
                        if self._end_edge == EdgeType.START:
                            self._end = end.start_point
                        else:
                            self._end = end.end_point
                    else:
                        raise TimeSpanCreateArgumentError(
                            "there is no span between start and end"
                        )

    def __str__(self) -> str:
        if self._type == SpanType.BETWEEN:
            return f"{self._start} - {self._end}"
        else:
            return f"{self._type} - {self._start}"

    def __repr__(self) -> str:
        return f"TimeSpan : {self.__str__()}"

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

    @staticmethod
    def occuresnces_in_period(
        time_span: TimeSpan, period_start: TimePoint, period_end: TimePoint
    ) -> Optional[List[TimeSpan]]:
        if time_span.type != SpanType.BETWEEN:
            raise TimeSpanOccurrenceError("time_span must be of type BETWEEN")
        else:
            occurrences: List[TimeSpan] = []
            span_start = time_span.start
            if time_span.end is not None:
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
            else:
                if start_occurrences is None or end_occurrences is None:
                    return None
                else:
                    start_occurrences_len = len(start_occurrences)
                    end_occurrences_len = len(end_occurrences)
                    if start_occurrences_len < 1 or end_occurrences_len < 1:
                        occurrences = []
                    if start_occurrences_len < end_occurrences_len:
                        start_occurrences = start_occurrences[:1]
                    else:
                        end_occurrences = end_occurrences[1:]
                    occurrences_pairs = zip(start_occurrences, end_occurrences)
                    occurrences = [
                        TimeSpan(
                            span_start,
                            start_edge,
                            span_end,
                            end_edge,
                            SpanType.BETWEEN,
                        )
                        for span_start, span_end in occurrences_pairs
                    ]
            return occurrences

    @staticmethod
    def occurrences_in_sapn(
        contained_span: TimeSpan, container_span: TimeSpan
    ) -> Optional[List[TimeSpan]]:

        try:
            return TimeSpan.occuresnces_in_period(
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
