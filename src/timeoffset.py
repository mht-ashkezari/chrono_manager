
from enum import Enum

import re
from typing import List, Optional, Tuple, Union
from __future__ import annotations

from frozendict import frozendict
from .timepoint import TimePoint
from .timespan import TimeSpan


OFFSET_MONTH_LENGTH = 30
OFFSET_YEAR_LENGTH = 365

class OffsetUnit(Enum):
    """
    Enum class for the time units.
    """
    YR = "YR"
    MH = "MH"
    WK = "WK"
    DY = "DY"    
    # WY = "WY"
    HR = "HR"
    ME = "ME"
    SD = "SD"











"""
OffsetUnitScope: dict[OffsetUnit, List[OffsetUnit]] = {
    OffsetUnit.SD: [OffsetUnit.ME],
    OffsetUnit.ME: [OffsetUnit.HR],
    OffsetUnit.HR: [OffsetUnit.DY, OffsetUnit.WY],

    OffsetUnit.WK: [OffsetUnit.YR],
    OffsetUnit.DY: [OffsetUnit.MH],
    OffsetUnit.MH: [OffsetUnit.YR],
}
"""


class TimeOffsetException(Exception):
    def init(self, message: str) -> None:
        super().init(message)


class TimeOffsetArgumentError(TimeOffsetException):
    def init(self, message: str) -> None:
        super().init(message)


class OffsetElement:

    def __init__(
            self, unit: Union[OffsetUnit, str],
            value: Optional[int],
            is_shift: Optional[bool] = False
            ) -> None:
        if isinstance(unit, str):
            self._unit, self._value, self._is_shift = OffsetElement.from_string(unit)
        elif isinstance(unit, OffsetUnit):
            if not value or value is None or is_shift is None:
                raise TimeOffsetArgumentError("Value must be provided for OffsetUnit")
            self._unit = unit
            self._value = value
            self._is_shift = is_shift

    def __str__(self):
        return f"OE({self.unit.value}{self.value})"

    def __repr__(self) -> str:
        return f"OffsetElement({self.unit.value}{self.value})"

    @classmethod
    def from_string(cls, element_string: str) -> Tuple[OffsetUnit, int, bool]:
        units_pattern = "|".join(unit.value for unit in OffsetUnit)
        pattern = f"({units_pattern})([-]?\d+|>[-]?\d+)"
        match = re.fullmatch(pattern, element_string)
        if not match:
            raise ValueError(f"Invalid time offset element string: {element_string}")
        
        unit_str, value_str = match.groups()
        
        # Check if the '>' symbol is present to determine if it's a shift
        is_shift = value_str.startswith('>')
        
        # Remove the '>' if it's a shift to get the numeric value
        if is_shift:
            value_str = value_str[1:]
        
        try:
            unit = OffsetUnit(unit_str)  # Convert the string to the OffsetUnit enum
        except ValueError:
            raise ValueError(f"Invalid OffsetUnit: {unit_str}")

        value = int(value_str)  # Convert the value to an integer

        return (unit, value, is_shift)

    @property
    def unit(self) -> OffsetUnit:
        return self._unit

    @unit.setter
    def unit(self, unit: OffsetUnit):
        self._unit = unit

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int):
        self._value = value

    @property
    def is_shift(self) -> bool:
        return self._is_shift

    @is_shift.setter
    def is_shift(self, is_shift: bool):
        self._is_shift = is_shift

    @property
    def representation(self) -> str:
        return (f"{self.unit.value}{self.value}"
                if not self.is_shift else f"{self.unit.value}>{self.value}")


class TimeOffset:
    OFFSET_UNIT_TO_SECONDS = {
        OffsetUnit.YR: 365 * 24 * 60 * 60,
        OffsetUnit.MH: 30 * 24 * 60 * 60,
        OffsetUnit.WK: 7 * 24 * 60 * 60,
        OffsetUnit.DY: 24 * 60 * 60,
        OffsetUnit.HR: 60 * 60,
        OffsetUnit.ME: 60,
        OffsetUnit.SD: 1
    }

    def __init__(
            self, scope: OffsetUnit,
            offset_elements: Union[str, List[OffsetElement]]
    ) -> None:
        if isinstance(offset_elements, str):
            self._elements = TimeOffset.from_string(offset_elements)
        elif (
            isinstance(offset_elements, list)
            and all(isinstance(elem, OffsetElement) for elem in offset_elements)
        ):
            self._elements = offset_elements
        else:
            raise ValueError("Invalid input: must be a string or a list of OffsetElement instances.")
        self._unify_elements()
        self._convert_to_seconds()
        self._shifs = [element for element in self._elements if element.is_shift]
        self._amounts = [element for element in self._elements if not element.is_shift]

    def _unify_elements(self):
        unified_elements = {}
        for element in self._elements:
            key = (element.unit, element.is_shift)
            if key in unified_elements:
                unified_elements[key].value += element.value
            else:
                unified_elements[key] = OffsetElement(
                    element.unit, element.value, element.is_shift
                    )

        self._elements = list(unified_elements.values())

    def _convert_to_seconds(self):
        total_seconds = 0
        for element in self._elements:
            if not element.is_shift:
                unit_in_seconds = TimeOffset.OFFSET_UNIT_TO_SECONDS[element.unit]
                total_seconds += element.value * unit_in_seconds
        self._total_seconds = total_seconds

    def __str__(self):
        return f"TimeOffset({self._elements})"

    def __repr__(self):
        return str(self)

    @classmethod
    def from_string(cls, offset_string: str) -> List[OffsetElement]:
        pattern = r"(SD|ME|HR|WK|DY|MH|YR)(>[-]?\d+|[-]?\d+)"
        matches = re.findall(pattern, offset_string)
        if not matches:
            raise ValueError(f"Invalid time offset string: {offset_string}")

        elements = []
        for unit_str, value_str in matches:
            unit = OffsetUnit[unit_str]
            is_shift = value_str.startswith('>')
            value = int(value_str[1:] if is_shift else value_str)
            elements.append(OffsetElement(unit, value, is_shift))
        return elements

    @property
    def elements(self) -> List[OffsetElement]:
        return self._elements

    @property
    def shifts(self) -> List[OffsetElement]:
        return self._shifs

    #TODO: add setter for amounts and shifts

    @property
    def total_seconds(self) -> int:
        return self._total_seconds
    
    @property
    def amounts(self) -> List[OffsetElement]:
        return self._amounts



