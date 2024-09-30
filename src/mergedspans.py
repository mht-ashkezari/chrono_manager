from __future__ import annotations
from typing import Dict, Optional, Union
from src.constants import SpanType, EdgeType
from src.timespan import TimeSpan, TimeSpanStringError
from src.timepoint import TimePoint, TimePointNotComparableError
from enum import Enum
import re

class MergedSapnExcption(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MergedSpanArgumentError(MergedSapnExcption):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MergedSpanImpossible(MergedSapnExcption):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MeregedTimeSpan:
    def __init__(
            self,
            start: Union[TimePoint, str],
            start_edge: Optional[EdgeType],
            end: Optional[TimePoint],
            end_edge: Optional[EdgeType],
            added_scope: Optional[int] = 1
        ) -> None:
        if isinstance(start, str):
            try:
                scope_str = re.search(r"#\d+$", start)
                added_scope = int(scope_str.group(0)[1:])
                span_params = TimeSpan.parse_time_span_string(start)
            except TimeSpanStringError as e:
                raise MergedSpanArgumentError(str(e)) from e
            else:
                start = span_params["start"]
                start_edge = span_params["start_edge"]
                end = span_params["end"]
                end_edge = span_params["end_edge"]
        elif (
            not isinstance(start, TimePoint) or
                (start_edge is None or end is None or end_edge is None or added_scope is None or added_scope < 1)):
            raise MergedSpanArgumentError(
                "start, start_edge, end, and end_edge must be provided and added_scope must be greater than 0"
                )
        else:
            try:
                point_compare = TimePoint.compare_points(start, end)
            except TimePointNotComparableError as e:
                raise MergedSpanArgumentError(str(e)) from e
            else:
                if isinstance(point_compare, int):
                    if point_compare == 1:
                        self._start_point = start
                        self._end_point = end
                        self._available_years = None
                    elif point_compare == -1:
                        raise MergedSpanArgumentError(
                            "start_point must be greater than end_point"
                            )
                    elif point_compare == 0:
                        raise MergedSpanArgumentError("Start and end points are the same")
                    else:
                        raise MergedSpanArgumentError("Invalid time points")
                if isinstance(point_compare, Dict):
                    greaters = point_compare["greater"]
                    if not greaters:
                        raise MergedSpanArgumentError(
                            "start_point must be greater than end_point at least in one year"
                            )
                    self._start_point = start
                    self._end_point = end
                    self._available_years = greaters

            


    