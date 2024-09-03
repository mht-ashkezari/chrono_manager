from __future__ import annotations
import re
from typing import Callable, Dict, List, Optional, Tuple, Union, cast
from .units_constants import UNITS, TimeUnitInfo


class TimeElement:

    _units: Dict[str, TimeUnitInfo] = UNITS

    def __init__(self, unit_name_or_string: str, value: Optional[int] = None):
        """
        Initialize a TimeElement instance.

        Args:
            unit_name_or_string (str): Either the name of the unit
                    (e.g., 'YR', 'ME', etc.) or a string representation
                    of the time unit.
            value (int, optional): The value of the unit if initializing
                    by unit name. Defaults to None.

        Raises:

            ValueError: If the string does not match any
            unit's default or alternative pattern or if the unit name is
            invalid.
        """
        method_name = TimeElement.__init__.__name__
        if not isinstance(unit_name_or_string, str):
            raise TypeError(
                f"{method_name}Expected 'unit_name_or_string' to be a string, "
                f"but got {type(unit_name_or_string).__name__}."
            )
        if value is not None and not isinstance(value, int):
            # fmt: off
            raise TypeError(
                f"Expected 'value' to be an integer"
                f", but got {type(value).__name__}."
            )
            # fmt: on
        if value is None:
            elemets, matched_substrings, unmatched_substrings = (
                self.parse_time_string_to_elements(unit_name_or_string)
            )
            if not elemets or len(elemets) > 1 or unmatched_substrings:
                # fmt: off
                raise ValueError(
                    f"{method_name}: Invalid time string for a TimeElement"
                    f" instance'{unit_name_or_string}'"
                )  # fmt: on
            else:
                self._element_unit = elemets[0].element_unit
                self._element_value = elemets[0].element_value
        else:
            if unit_name_or_string not in self._units:
                raise ValueError(
                    f"{method_name}: Invalid unit name '{unit_name_or_string}'"
                )

            else:
                self._element_unit = unit_name_or_string
                try:
                    self._validate_value(unit_name_or_string, value)
                except ValueError as ve:
                    raise ValueError(
                        f"{method_name}: Error validating value '{value}' "
                        f" for unit'{unit_name_or_string}'"
                    ) from ve
                else:
                    self._element_value = value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TimeElement):
            return (
                self.element_unit == other.element_unit
                and self.element_value == other.element_value
            )
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, TimeElement):
            if self.element_unit != other.element_unit:
                raise ValueError(
                    f"Cannot compare TimeElement objects with different units:"
                    f" {self.element_unit} and {other.element_unit}"
                )
            return self.element_value < other.element_value
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, TimeElement):
            return self.__eq__(other) or self.__lt__(other)
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, TimeElement):
            return not self.__le__(other)
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, TimeElement):
            return not self.__lt__(other)
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, TimeElement):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash((self.element_unit, self.element_value))

    def __str__(self) -> str:
        return f"{self._element_unit}={self._element_value}"

    def __repr__(self) -> str:
        return f"TimeElement('{self._element_unit}', {self._element_value})"

    @property
    def over_join_units(self) -> List[str]:
        """
        Returns a list of units that can be
        joined with the current element unit.

        Returns:
            List[str]: A list of unit names.
        """
        return cast(List[str], self._units[self._element_unit]["over_join_units"])

    @property
    def under_join_units(self) -> List[str]:
        """
        Returns a list of units that can be joined under the
        current element unit.

        Returns:
            List[str]: A list of unit names.
        """
        return cast(List[str], self._units[self._element_unit]["under_join_units"])

    @property
    def element_unit(self) -> str:
        """
        Returns the unit of the element.

        Return:
            str: The unit of the element.
        """
        return self._element_unit

    @property
    def allowed_values_type(self) -> str:
        """
        Returns the value type of the allowed values for the element unit.

        Returns:
            str: The value type of the allowed values.
        """
        return cast(str, self._units[self._element_unit]["value_type"])

    @property
    def default_representation(self) -> str:
        """
        Returns the default representation of the element value.

        Returns:
            str: The default representation of the element value.
        """
        default_repr_callable = cast(
            Callable[[int], str],
            self._units[self._element_unit]["default_representation"],
        )

        return default_repr_callable(self._element_value)

    @property
    def alternative_representation(self) -> str:
        """
        Returns the alternative representation of the element
        value based on the element unit.

        Returns:
            str: The alternative representation of the element value.
        """
        default_repr_callable = cast(
            Callable[[int], str],
            self._units[self._element_unit]["alternative_representation"],
        )
        return default_repr_callable(self._element_value)

    @property
    def element_value(self) -> int:
        """
        Returns the value of the element.

        Returns:
            int: The value of the element.
        """
        return self._element_value

    @element_value.setter
    def element_value(self, value: int) -> None:
        """
        Set the value of the element.

        Parameters:
            value (int): The value to be set.

        Raises:
            TypeError: If the value is not an integer.
            ValueError: If the value is not valid for the element unit.
        """
        # fmt: off
        try:
            self._validate_value(self._element_unit, value)
        except ValueError as ve:
            raise ValueError(
                f"Error validating value '{value}'" 
                f"for unit '{self._element_unit}'"
            ) from ve
        else:
            self._element_value = value

    @classmethod
    def unit_values_to_end_scope(
        cls, unit_name: str, start_value: int, month: Optional[int] = None
    ) -> List[int]:
        """
        Returns a list of values for a given unit that
        will reach the maximum value for the unit.

        Args:
            unit_name (str): The name of the unit.
            start_value (int): The starting value for the unit.

        Returns:
            List[int]: A list of values that will reach the maximum value
                for the unit.
        """
        if not cls._units.get(unit_name):
            raise ValueError(f"Invalid unit name '{unit_name}'")
        callable_val_scope_dy = cast(
            Callable[[int, Union[str, None]], List[int]],
            cls._units[unit_name]["values_to_end_scope"],
        )
        callable_val_scope = cast(
            Callable[[int], List[int]],
            cls._units[unit_name]["values_to_end_scope"],
        )
        if unit_name == "DY":
            allowed_values: Dict[str, int] = cast(
                Dict[str, int], cls._units["MH"]["allowed_values"]
            )
            month_name = next(
                (k for k, v in allowed_values.items() if v == month),
                None,
            )
            return callable_val_scope_dy(start_value, month_name)
        else:
            return callable_val_scope(start_value)

    # fmt: off
    @staticmethod
    def get_max_value(
            unit_name: str, month: Union[str, int, None] = None) -> int:
        # fmt: on
        method_name = TimeElement.get_max_value.__name__
        unit_info = TimeElement._units.get(unit_name, {})
        unit_allowed_values = cast(Dict[str, int], unit_info.get("allowed_values", {}))
        if not unit_info:
            raise ValueError(f"{method_name}: Invalid unit name '{unit_name}'")
        if unit_name == "DY":
            if month:
                if isinstance(month, int):
                    month_names = unit_allowed_values.keys()
                    month = cast(str, list(month_names)[month - 1])
                month_info = cast(Dict[str, int], unit_allowed_values.get(month))
                if month_info:
                    return cast(int, month_info["max"])
                else:
                    # fmt: off
                    raise ValueError(
                        f"{method_name}: Invalid month value '{month}'")
                    # fmt: on
            else:
                return 31
        elif unit_info and cast(str, unit_info["value_type"]) == "range":
            return cast(int, unit_allowed_values["max"])
        elif unit_info and unit_info["value_type"] == "list":
            return max(
                cast(
                    List[int],
                    cast(Dict[str, int], unit_allowed_values).values()
                )
            )
        # If none of the conditions are met, raise an error
        raise ValueError(f"Cannot determine max value for unit '{unit_name}'")

    @staticmethod
    def get_min_value(unit_name: str) -> int:
        method_name = TimeElement.get_min_value.__name__
        unit_info = TimeElement._units.get(unit_name, {})
        unit_allowed_values = cast(
            Dict[str, int],
            unit_info.get("allowed_values", {})
        )
        if not unit_info:
            raise ValueError(f"{method_name}: Invalid unit name '{unit_name}'")
        elif unit_info and unit_info["value_type"] == "range":
            return cast(int, unit_allowed_values["min"])
        elif unit_info and unit_info["value_type"] == "list":
            return min(cast(List[int], unit_allowed_values.values()))
        # If none of the conditions are met, raise an error
        raise ValueError(f"Cannot determine min value for unit '{unit_name}'")

    @staticmethod
    def _validate_value(unit_name: str, value: int) -> bool:
        """
        Validates the value for a given unit name.

        Args:
            unit_name (str): The name of the unit.
            value (int): The value to be validated.

        Raises:
            TimeElementValueInvalidError: If the value is not within the
            allowed range or not in the allowed list.

        Returns:
            bool: True if the value is valid, False otherwise.
        """
        method_name = TimeElement._validate_value.__name__
        unit_info = TimeElement._units[unit_name]
        unit_allowed_values = cast(
            Dict[str, int],
            unit_info.get("allowed_values", {})
        )
        if unit_info["value_type"] == "range":
            if unit_name == "DY":
                min_val, max_val = 1, 31
            else:
                min_val, max_val = (
                    unit_allowed_values["min"],
                    unit_allowed_values["max"],
                )

            if not (min_val <= value <= max_val):
                # fmt: off
                raise ValueError(
                    f"{method_name}: Invalid value '{value}'"
                    f" for unit '{unit_name}'")
                # fmt: on
        elif (
            unit_info["value_type"] == "list" and
            value not in unit_allowed_values.values()
        ):
            raise ValueError(
                # fmt: off
                f"{method_name}: Invalid value "
                f"'{value}' for unit '{unit_name}'"
            )
            # fmt: on
        return True

    @staticmethod
    def parse_time_string_to_elements(
        time_string: str,
    ) -> Tuple[List[TimeElement], List[str], List[str]]:
        """
        Parses a given time string into its constituent elements, identifying
        and categorizing matched and unmatched substrings.

        This method processes the input `time_string` by sequentially
        attempting to match it against predefined time element patterns.
        The time elements are defined by `TimeElement._units`, where each
        unit has a specific pattern, value type, and allowed values.
        The method attempts to extract these time elements, validate
        them, and then categorize the substrings of the input string into
        matched elements, matched substrings, and unmatched substrings.

        Args:
            time_string (str): The input string representing a time or
                                duration that needs to be parsed.

        Returns:
            Tuple [ List[ TimeElement ] , List[ str ], List[ str ] ]:
                - List of `TimeElement` objects that represent the matched
                    time elements.
                - List of substrings from the input string that were
                    successfully matched with the time elements.
                - List of substrings from the input string that could not be
                    matched and were left as unmatched.

        Raises:
            ValueError: If a digit cannot be extracted from a substring
                expected to contain a numerical value, or if an invalid string
                value is encountered for a time unit.

        """
        func_name = TimeElement.parse_time_string_to_elements.__name__
        matched_elements = []
        matched_substrings = []
        unmatched_substrings = []

        remaining_string = time_string

        while remaining_string:
            match_found = False
            for unit_key, unit_info in TimeElement._units.items():
                unit_alt_pattern = cast(str, unit_info["alternative_pattern"])
                unit_def_pattern = cast(str, unit_info["default_pattern"])
                unit_pattern = f"({unit_def_pattern}|{unit_alt_pattern})"

                # Try to match with default pattern
                # fmt: off
                default_match = re.match(
                    unit_pattern, remaining_string)
                # fmt: on
                if default_match:  # or alternative_match:
                    # fmt: off
                    match = default_match
                    assert match is not None, "Match should not be None"
                    matched_string = match.group()
                    # fmt: on
                    # Extract the value from the matched string
                    if unit_info["value_type"] == "range":
                        digit_match = re.search(r"\d+", matched_string)
                        if digit_match:
                            value = int(digit_match.group())
                        else:
                            # fmt: off
                            raise ValueError(
                                f"{func_name}: Could not extract digits from"
                                f"{matched_string} for unit '{unit_key}'"
                            )
                            # fmt: on
                    elif unit_info["value_type"] == "list":
                        value_str = matched_string
                        allowed_values = cast(
                            Dict[str, int],
                            unit_info["allowed_values"]
                        )
                        value = cast(int, allowed_values.get(value_str))

                        if value is None:
                            digit_match = re.search(r"\d+", value_str)
                            if digit_match:
                                value = int(digit_match.group())
                            else:
                                # fmt: off
                                raise ValueError(
                                    f"{func_name}: Invalid string value '{value_str}'"
                                    f"for unit '{unit_key}'"
                                )
                                # fmt: on
                    # Validate and create TimeElement object
                    try:
                        is_valid = TimeElement._validate_value(unit_key, value)
                    except ValueError as ve:
                        # fmt: off
                        raise ValueError(
                            f"{func_name}:Error validating value '{value}' for"
                            f" unit '{unit_key}'"
                        ) from ve
                        # fmt: on
                    else:
                        if value is not None and is_valid:
                            matched_elements.append(TimeElement(unit_key, value))
                            # fmt: off
                            matched_substrings.append(matched_string)
                            remaining_string = (
                                remaining_string[len(matched_string):])
                            # fmt: on
                            match_found = True
                            break

            if not match_found:
                # No match found for the beginning of the string,
                # consider it unmatched
                unmatched_substrings.append(remaining_string[0])
                remaining_string = remaining_string[1:]

        return matched_elements, matched_substrings, unmatched_substrings
