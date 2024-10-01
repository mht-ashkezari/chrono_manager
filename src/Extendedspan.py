from __future__ import annotations
from typing import Dict, List, Optional, Union
from src.constants import SpanType, EdgeType
from src.timespan import TimeSpan, TimeSpanStringError
from src.timepoint import TimePoint, TimePointNotComparableError
from enum import Enum
import re


class ExtendedSpanException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ExtendedSpanArgumentError(ExtendedSpanException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ExtendedSpanImpossibleError(ExtendedSpanException):
    def __init__(self, message: str) -> None:
        super().__init__(message)

class ExtendedSpanStringError(ExtendedSpanException):
    def __init__(self, message: str) -> None:
        super().__init__(message)

class ExtenedTimeSpan:
    def __init__(
            self,
            start: Union[TimePoint, str],
            start_edge: Optional[EdgeType],
            end: Optional[TimePoint],
            end_edge: Optional[EdgeType],
            subsequent_scopes: Optional[int] = 1
        ) -> None:
        if isinstance(start, str):
            try:
                start_params = ExtenedTimeSpan.from_string(start)
            except ExtendedSpanStringError as e:
                raise ExtendedSpanArgumentError(str(e)) from e
            else:
                start = start_params["start"]
                start_edge = start_params["start_edge"]
                end = start_params["end"]
                end_edge = start_params["end_edge"]
                subsequent_scopes = start_params["subsequent_scopes"]
        elif (
            not isinstance(start, TimePoint) or
                (start_edge is None or
                    end is None or end_edge is None or
                    subsequent_scopes is None or subsequent_scopes < 1)
                    ):
            raise ExtendedSpanArgumentError(
                "start, start_edge, end, and end_edge must be"
                "provided and added_scope must be greater than 0"
                )
        
        try:
            point_compare = TimePoint.compare_points(start, end)
        except TimePointNotComparableError as e:
            raise ExtendedSpanArgumentError(str(e)) from e
        else:
            if isinstance(point_compare, int):
                if point_compare != 1 and point_compare != 1:
                    if point_compare == 0:
                        raise ExtendedSpanArgumentError(
                            "Start and end points"
                            "can not be the same")
                    else:
                        raise ExtendedSpanArgumentError("Invalid time points")
            if isinstance(point_compare, Dict):
                greaters = point_compare["greater"]
                if not greaters:
                    raise ExtendedSpanArgumentError(
                        "start_point must be greater"
                        "than end_point at least in one year"
                        )

            self._start_point = start
            self._end_point = end
            self._available_years = greaters
            self._subsequent_scopes = subsequent_scopes
            self._start_edge = start_edge
            self._end_edge = end_edge
            self.start_span = TimeSpan(start=start, start_edge=start_edge, span_type=SpanType.AFTER)
            self.end_span = TimeSpan(start=end, start_edge=end_edge, span_type=SpanType.BEFORE)

    def __str__(self) -> str:
        return f"ES({self.default_represenantion})"

    def __repr__(self) -> str:
        return f"ExtendedSpan({self.default_represenantion})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExtenedTimeSpan):
            return NotImplemented
        return (
            self.start_point == other.start_point and
            self.end_point == other.end_point and
            self.start_edge == other.start_edge and
            self.end_edge == other.end_edge and
            self.subsequent_scopes == other.subsequent_scopes
        )

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, ExtenedTimeSpan):
            return NotImplemented
        return (
            self.start_point != other.start_point or
            self.end_point != other.end_point or
            self.start_edge != other.start_edge or
            self.end_edge != other.end_edge or
            self.subsequent_scopes != other.subsequent_scopes
        )

    def __hash__(self) -> int:
        return hash((
            self.start_point,
            self.end_point,
            self.start_edge,
            self.end_edge,
            self.subsequent_scopes
        ))

    @staticmethod
    def to_string(ext_span: ExtenedTimeSpan,is_default_repr:bool = True) -> str:
        return (f"{ext_span.start_span.default_represenantion}"
                f"{ext_span.end_span.default_represenantion[1:]}"
                f"#{ext_span._subsequent_scopes}" if is_default_repr 
                else
                f"{ext_span.start_span.alternative_represenantion}"
                f"{ext_span.end_span.alternative_represenantion[1:]}"
                f"#{ext_span._subsequent_scopes}")

    @staticmethod
    def from_string(ext_span_str: str) -> Dict:
        try:
            scope_str = re.search(r"#\d+$", ext_span_str)
            span_params = TimeSpan.parse_time_span_string(ext_span_str)
        except TimeSpanStringError as e:
            raise ExtendedSpanStringError(str(e)) from e
        else:
            if scope_str is None:
                raise ExtendedSpanStringError(
                    "Subsequent scopes must be provided with a hashtag symbol (#) "
                    "followed by a number at the end of the start string."
                )
            else:
                subsequent_scopes = int(scope_str.group(0)[1:])
            start = span_params["start"]
            start_edge = span_params["start_edge"]
            end = span_params["end"]
            end_edge = span_params["end_edge"]
            return {
                "start": start,
                "start_edge": start_edge,
                "end": end,
                "end_edge": end_edge,
                "subsequent_scopes": subsequent_scopes
            }

    @property
    def alternative_represenantion(self) -> str:
        return ExtenedTimeSpan.to_string(self, is_default_repr=False)

    @property
    def default_represenantion(self) -> str:
        return ExtenedTimeSpan.to_string(self, is_default_repr=True)

    @property
    def start_point(self) -> TimePoint:
        return self._start_point

    @property
    def end_point(self) -> TimePoint:
        return self._end_point

    @property
    def available_years(self) -> Optional[List[int]]:
        return self._available_years
    
    @property
    def subsequent_scopes(self) -> int:
        return self._subsequent_scopes
    
    @property
    def start_edge(self) -> EdgeType:
        return self._start_edge
    
    @property
    def end_edge(self) -> EdgeType:
        return self._end_edge
    
