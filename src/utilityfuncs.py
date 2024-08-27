from __future__ import annotations

from typing import Optional, Tuple, List, Union, Dict
from datetime import datetime, timedelta
import calendar
from .timeelement import TimeElement
from .units_constants import START_YEAR, END_YEAR, units_sequence
from .configs import YEARS_WITH_53_WEEKS, CompareSequnce


def days_to_year_start_iso(
    iso_year: int, iso_week: int, iso_weekday: Union[str, int, None]
):
    # Convert ISO year, week, and day to a Gregorian date
    if iso_weekday is None or isinstance(iso_weekday, str):
        iso_weekday = 1
    iso_date = datetime.strptime(f"{iso_year} {iso_week} {iso_weekday}", "%G %V %u")

    # Determine the first day of the ISO year
    jan_4 = datetime(
        iso_year, 1, 4
    )  # January 4th is always in the first week of the ISO year
    iso_year_start = jan_4 - timedelta(
        days=jan_4.isoweekday() - 1
    )  # Find the Monday of that week

    # Calculate difference from the actual ISO year start
    return (iso_date - iso_year_start).days


def days_to_year_start_gregorian(year: int, month: int, day: Union[str, int, None]):
    # Gregorian date
    if day is None or isinstance(day, str):
        day = 1
    gregorian_date = datetime(year, month, day)
    # Calculate difference from year start
    year_start = datetime(year, 1, 1)
    return (gregorian_date - year_start).days


def is_iso_greg_compare_consistent(
    treshold: int,
    iso_year: int,
    iso_week: int,
    iso_weekday: Union[str, int, None],
    year: int,
    month: int,
    day: Union[str, int, None],
) -> bool:

    iso_days = days_to_year_start_iso(iso_year, iso_week, iso_weekday)
    gregorian_days = days_to_year_start_gregorian(year, month, day)
    difference = abs(iso_days - gregorian_days)

    if difference > treshold:
        # Consistent comparison across alll years
        return True
    else:
        # Need to compare for each year
        return False


def leap_years_between(start_year, end_year):
    """
    Calculates all leap years between two given years.

    Args:
        start_year: The starting year.
        end_year: The ending year.

    Returns:
        A list of leap years between the given years.
    """

    leap_years = []
    for year in range(start_year, end_year + 1):
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            leap_years.append(year)
    return leap_years


def find_year_with_53_weeks(start_year=1800, end_year=2100) -> List[int]:
    """
    Finds and returns a list of years that have 53 weeks.

    Args:
        start_year (int): The starting year to search for 53-week years
        (inclusive). Default is 1800.

        end_year (int): The ending year to search for 53-week years
        (inclusive). Default is 2100.

    Returns:
    - List[int]: A list of years that have 53 weeks.
    """
    years = []
    for year in range(start_year, end_year + 1):
        last_day_of_year = datetime(year, 12, 31)
        iso_year, last_week, last_weekday = last_day_of_year.isocalendar()

        if last_week == 53:
            years.append(year)

    return years


def find_intersection(
    intlist1: Optional[List[int]], intlist2: Optional[List[int]]
) -> Optional[List[int]]:
    """
    Find the intersection of two lists of integers. None is considered as
    the universal set in args and returns

    Args:
        intlist1 (Optional[List[int]]): The first list of integers.
        intlist2 (Optional[List[int]]): The second list of integers.

    Returns:
        Optional[List[int]]: The intersection set of integer lists given as arguments
                            or None (universal set) if both lists are None
                            (universal set).
    """
    if intlist1 is None and intlist2 is None:
        return None  # Both lists are None, return None (universal set)

    if intlist1 is None:
        return sorted(intlist2)  # type: ignore  # Return the sorted second list

    if intlist2 is None:
        return sorted(intlist1)  # Return the sorted first list

    # Both lists are not None, return their intersection sorted
    intersection = [y for y in intlist1 if y in intlist2]
    return sorted(intersection)


def _set_complete_elements_values(
    complete_elements: List[Union[int, str]], default_unit_values: List[int]
) -> List[int]:
    """
    Sets the values of complete_elements based on the default_unit_values.

    Args:
        complete_elements (List[Union[int, str]]): The list of elements to set
                                                    values for.
        default_unit_values (List[int]): The list of default values to use.

    Returns:
        List[int]: The list of set values.

    Raises:
        ValueError: If default_unit_values does not contain exactly 6 integer values.
    """
    func_name = _set_complete_elements_values.__name__

    if len(default_unit_values) != 6:
        # fmt: off
        raise ValueError(
            f"{func_name}: default_unit_values must contain exactly"
            f" 6 integer values")
        # fmt: on
    set_values = []
    for index, el in enumerate(complete_elements):
        if isinstance(el, str):
            set_values.append(default_unit_values[index])
        else:
            set_values.append(el)

    return set_values


def get_element_by_unit_from_elements(
    unit_name: str, elements: List[TimeElement]
) -> Optional[TimeElement]:
    """
    Retrieves a `TimeElement` from a list based on the unit name.

    Args:
        unit_name (str): The name of the unit to search for.
        elements (List[TimeElement]): A list of `TimeElement` objects.

    Returns: Optional [TimeElement, None]:
        The TimeElement object if found, otherwise None.

    """

    for element in elements:
        if element.element_unit == unit_name:
            return element
    else:
        return None


def get_value_by_unit_from_elements(
    unit_name: str, elements: List[TimeElement]
) -> Tuple[Optional[int], Optional[int]]:
    """
    Returns the unit value from a list of `TimeElement` objects.

    Args:
        unit_name (str): The name of the unit to search for.
        elements (List[TimeElement]): A list of `TimeElement` objects.

    Returns:
        Tuple [Optional [ int , None ], Optional [ int , None ] ]:
            A tuple containing:
            - A boolean indicating whether the unit was found.
            - The value of the unit if found, otherwise `None`.
            - The index of the element in the list if found, otherwise `None`.

    """

    for index, element in enumerate(elements):
        if element.element_unit == unit_name:
            return element.element_value, index
    else:
        return None, None


def add_element_to_elements(
    element_added: TimeElement, elements: List[TimeElement]
) -> Optional[List[TimeElement]]:
    """
    Adds an element to a list of time elements.

    Args:
        element_added (TimeElement): The time element to be added.
        elements (List[TimeElement]): The list of time elements.

    Returns:
        Optional [ List [ TimeElement ], None ]:
        The updated list of elements if the element was added successfully,
        None if the element unit already exists in the list.

    """

    result_elements = elements.copy()
    if not result_elements:
        return [element_added]

    if element_added.element_unit in [el.element_unit for el in elements]:
        return None

    result_elements.append(element_added)
    return result_elements


def find_duplicate_units(elements: List[TimeElement]) -> List[str]:
    """
    Identifies duplicate units in a list of `TimeElement` objects.

    Args:
        elements (List[TimeElement]): A list of `TimeElement` objects.

    Returns:
        List[str]:  A list of duplicate unit names.
    """

    seen = set()
    duplicates = []
    for element in elements:
        if element.element_unit in seen:
            duplicates.append(element.element_unit)
        else:
            seen.add(element.element_unit)
    return duplicates


# fmt: off
def get_elements_sequence(elements: List[TimeElement]) -> Optional[Tuple[str, ...]]:
    # fmt: on
    """
    Returns the sequence of units if all elements in the given list have their
    units in the same sequence. If no match is found, returns None.

    Args:
        - elements (List[TimeElement]): A list of TimeElement objects.

    Returns:
        - Optional [ Tuple [ str, ...] , None ]:
        A tuple representing the sequence of units if all elements have their
        units in the same sequence, or None if no match is found.
    """
    for key, value_tuple in units_sequence.items():
        if all(element.element_unit in value_tuple for element in elements):
            return value_tuple

    # If no match is found after the loop, return None
    return None


def get_unit_index_in_elements(
    unit_name: str, elements: List[TimeElement]
) -> Optional[int]:
    """
    Returns the index of a unit in a list of TimeElement objects.

    Args:
        unit_name (str): The name of the unit to search for.
        elements (List[TimeElement]): A list of TimeElement objects.

    Returns: Optional[ int, None ]:
            The index of the unit if found, otherwise None.
    """

    for index, element in enumerate(elements):
        if element.element_unit == unit_name:
            return index
    else:
        return None


""" Top-Level Functions """


def is_ordered_elements(elements: List[TimeElement]) -> bool:
    """
    Check if the given list of TimeElements is ordered.

    Args:
        elements (List[TimeElement]): The list of TimeElements to be checked.

    Returns:
        bool: True if the elements are ordered.

    Raises:
        ValueError: If the elements are not in a valid sequence,
                    have duplicate units, have missing units, have not
                    valid values or are not sorted by sequence.
    """

    func_name = is_ordered_elements.__name__
    if get_elements_sequence(elements) is None:
        raise ValueError(f"{func_name}: elements must be in a valid sequence")
    if find_duplicate_units(elements):
        # fmt: off
        raise ValueError(
            f"{func_name}: elements must not have duplicate units")
    sorted_elements, missing = (
        sort_elements_by_sequence(elements))
    if missing:
        raise ValueError(
            f"{func_name}: elements have missing units : {missing}")
    # fmt: on
    try:
        check_elements_validity(elements)
    except ValueError as e:
        raise ValueError(f"{func_name}: {e}")

    if sorted_elements != elements:
        raise ValueError(f"{func_name}: elements must be sorted by sequence")
    return True


def add_element_to_ordered_elements(
    element_added: TimeElement, elements: List[TimeElement]
) -> List[TimeElement]:
    """
    Adds an element to a list of ordered elements based on its unit.

    Args:
        element_added (TimeElement): The element to be added.
        elements (List[TimeElement]): The list of ordered elements.

    Returns:
        List[TimeElement]: The updated list of ordered elements.

    Raises:
        ValueError: If the list of elements is not ordered.
        ValueError: If the element unit is already present in the list.
        ValueError: If the element unit is not above or below the existing elements.
        ValueError: If the resulting elements is not ordered.
    """

    func_name = add_element_to_ordered_elements.__name__

    result_elements = elements.copy()
    # Handle empty list case
    if not elements:
        return [element_added]
    try:
        is_ordered_elements(elements)
    except ValueError as e:
        raise ValueError(f"{func_name}:argument elements:{e}")
    else:
        if element_added.element_unit in [el.element_unit for el in elements]:
            raise ValueError(
                f"{func_name}: The element unit {element_added.element_unit}"
                f"is already in the list")
        else:
            if element_added.element_unit in elements[0].over_join_units:
                result_elements.insert(0, element_added)
            elif element_added.element_unit in elements[-1].under_join_units:
                result_elements.append(element_added)
            else:
                raise ValueError(
                    f"{func_name}: The element unit {element_added.element_unit}"
                    f" is not above or below unit of the existing elements"
                )
            try:
                is_ordered_elements(result_elements)
            except ValueError as e:
                raise ValueError(f"{func_name}:result elements:{e}")
        return result_elements


def remove_element_from_ordered_elements(
    element_remove: TimeElement, elements: List[TimeElement]
) -> List[TimeElement]:
    """
    Remove an element from a list of ordered elements.

    Args:
        element_remove (TimeElement): The element to be removed.
        elements (List[TimeElement]): The list of ordered elements.

    Returns:
        List[TimeElement]: The updated list of ordered elements after removing
                            the specified element.

    Raises:
        ValueError: If the elements are not ordered.
        ValueError: If the specified element is not present in the elements.
        ValueError: If the specified element is not the first or last element
                    in the elements.
        ValueError: If the resulting elelments is empty.
        ValueError: If the resulting elements are not ordered.
    """

    func_name = remove_element_from_ordered_elements.__name__
    result_elements = []
    try:
        is_ordered_elements(elements)
    except ValueError as e:
        raise ValueError(f"{func_name}:arguments elements:{e}")
    else:
        if element_remove not in elements:
            raise ValueError(
                f"{func_name}: The element must be"
                f" removed {element_remove} is not in the elements"
            )
        if element_remove == elements[0] or element_remove == elements[-1]:
            elements.remove(element_remove)
            result_elements = elements
        else:
            raise ValueError(
                f"{func_name}: The element unit {element_remove} must be"
                f" first ot last unit in the elements"
            )
        if not result_elements:
            raise ValueError(
                f"{func_name}: The result list must have at least one element"
            )
        try:
            is_ordered_elements(result_elements)
        except ValueError as e:
            raise ValueError(f"{func_name}:result elements:{e}")
        else:
            return result_elements


def remove_unit_from_ordered_elements(
    unit_removed: str, elements: List[TimeElement]
) -> List[TimeElement]:
    """
    Remove the specified unit from the list of ordered elements.

    Args:
        unit_removed (str): The unit to be removed.
        elements (List[TimeElement]): The list of ordered elements.

    Returns:
        List[TimeElement]: The updated list of ordered elements
        after removing the specified unit.

    Raises:
        ValueError: If the elements are not ordered.
        ValueError: If the specified unit is not in the elements.
        ValueError: If the specified unit is not the first or
                    last unit in the elements.
        ValueError: If the result elements is empty.
        ValueError: If the result elements are not ordered.
    """

    func_name = remove_unit_from_ordered_elements.__name__
    result_elements = []
    try:
        is_ordered_elements(elements)
    except ValueError as e:
        raise ValueError(f"{func_name}:argument elements:{e}")
    else:
        if unit_removed not in [el.element_unit for el in elements]:
            raise ValueError(
                f"{func_name}: The element unit {unit_removed} is not in the elements"
            )
        if (
            unit_removed == elements[0].element_unit
            or unit_removed == elements[-1].element_unit
        ):
            result_elements = [el for el in elements if el.element_unit != unit_removed]
        else:
            raise ValueError(
                f"{func_name}: The element unit {unit_removed} "
                f"must be first or last unit in the elements"
            )
        if not result_elements:
            raise ValueError(
                f"{func_name}: The result list must have at least one element"
            )
        try:
            is_ordered_elements(result_elements)
        except ValueError as e:
            raise ValueError(f"{func_name}:result elements:{e}")
        else:
            return result_elements


def update_element_in_ordered_elements(
    element_updated: TimeElement, elements: List[TimeElement]
) -> List[TimeElement]:
    """
    Update an element in a list of ordered elements.

    Args:
        element_updated (TimeElement): The element to be updated.
        elements (List[TimeElement]): The list of ordered elements.

    Returns:
        List[TimeElement]: The updated list of ordered elements.

    Raises:
        ValueError: If the list of elements is not ordered.
        ValueError: If the element to be updated is not in the elements.
        ValueError: If the updated list of elements is not ordered.
    """

    func_name = update_element_in_ordered_elements.__name__

    try:
        is_ordered_elements(elements)
    except ValueError as e:
        raise ValueError(f"{func_name}:argument elements:{e}")
    else:

        updated_elements = elements.copy()
        if element_updated not in elements:
            # fmt : off
            raise ValueError(
                f"{func_name}: The element {element_updated} is not "
                "in the elements"
            )
        else:
            index = (
                get_unit_index_in_elements(
                    element_updated.element_unit, elements)
            )
            if index is None:
                raise ValueError(
                    f"{func_name}: The element unit "
                    f"{element_updated.element_unit} is not in the elements"
                )
            # fmt : on
            updated_elements[index] = element_updated
            try:
                is_ordered_elements(updated_elements)
            except ValueError as e:
                raise ValueError(f"{func_name}:updated elements:{e}")
            else:
                return updated_elements


def update_unit_in_ordered_elements(
    unit_updated: str, value_updated: int, elements: List[TimeElement]
) -> List[TimeElement]:
    """
    Update the value of a specific unit in a list of ordered elements.

    Args:
        unit_updated (str): The unit to be updated.
        value_updated (int): The new value for the unit.
        elements (List[TimeElement]): The list of ordered elements.

    Returns:
        List[TimeElement]: The updated list of ordered elements.

    Raises:
        ValueError: If the elements are not ordered.
        ValueError: If the unit to be updated is not in the list.
        ValueError: If the unit to be updated is not in the elements.
        ValueError: If the updated elements are not ordered.
    """

    func_name = update_unit_in_ordered_elements.__name__

    try:
        is_ordered_elements(elements)
    except ValueError as e:
        raise ValueError(f"{func_name}:argument elements:{e}")
    else:
        updated_elements = elements.copy()
        if unit_updated not in [el.element_unit for el in elements]:
            raise ValueError(
                f"{func_name}: The element unit {unit_updated} is not in the list"
            )
        else:
            index = get_unit_index_in_elements(unit_updated, elements)
            if index is None:
                raise ValueError(
                    f"{func_name}: The element unit "
                    f"{unit_updated} is not in the elements"
                )
            updated_elements[index].element_value = value_updated
            try:
                is_ordered_elements(updated_elements)
            except ValueError as e:
                raise ValueError(f"{func_name}:updated elements:{e}")
            else:
                return updated_elements


def is_elements_leap(elements: List[TimeElement]) -> bool:
    """
    Check if the given list of TimeElement objects represents a leap year.

    Args:
        elements (List[TimeElement]): A list of TimeElement objects.

    Returns:
        bool: True if the list of TimeElement objects represents a leap year,
                False otherwise.
    """

    year_element = get_value_by_unit_from_elements("YR", elements)[0]
    month_element = next(
        (e.element_value for e in elements if e.element_unit == "MH"), None
    )
    day_element = next(
        (e.element_value for e in elements if e.element_unit == "DY"), None
    )

    # If both month and day are present, check if it's a valid date
    if month_element and day_element:
        try:
            datetime(
                year=year_element if year_element else 2000,
                month=month_element,
                day=day_element,
            )
        except ValueError:
            return False  # Invalid date

    if year_element is not None:
        return calendar.isleap(year_element)
    elif month_element == 2 and day_element == 29:
        return True
    return False


def what_is_sequence(elements: List[TimeElement]) -> Optional[str]:
    """
    Determine the sequence type (Gregorian or ISO) based on
        the provided TimeElement objects.

    Args:
        elements (List[TimeElement]): A list of TimeElement objects.

    Returns:
        str: The sequence type ('gregorian' or 'iso'). return None if elements
            is empty or its unitsare not in a valid sequence.
    """

    if not elements:
        return None
    # Get the units of elements found in a sequence of units_sequence and then
    # check if found units are the same as the elements
    for seq_name, seq_units in units_sequence.items():
        matched_units = [
            element.element_unit
            for element in elements
            if element.element_unit in seq_units
        ]

        # Check if all elements are in the correct order and match the
        # expected units for the sequence
        if matched_units == [el.element_unit for el in elements]:
            return seq_name

    # If no valid sequence is found
    return None


def sort_elements_by_sequence(
    elements: List[TimeElement],
) -> Tuple[Union[List[Union[TimeElement, str]], None], List[str]]:
    """
    Sorts the elements by their sequence and returns the sorted elements along
        with missing indicator and units.

    Args:
        elements (List[TimeElement]): The list of TimeElement objects to
        be sorted.

    Returns:
        Tuple [ Union[ List [ TimeElement,None ],None ], bool, List [ str ] ]:
        - A tuple containing:
        - A list sorted elements and name of missing units based on the
            valid sequence,
        - A list of missing units.
        - None and an empty list if the elements is empty or not in a valid sequence,
    """
    if not elements:
        return None, []
    sequence = get_elements_sequence(elements)
    if sequence is None:
        return None, []
    index_map = {unit: idx for idx, unit in enumerate(sequence)}
    sorted_elements = sorted(
        elements, key=lambda element: index_map.get(
            element.element_unit, float("inf"))
    )
    start_index = sequence.index(sorted_elements[0].element_unit)
    end_index = sequence.index(sorted_elements[-1].element_unit)
    # Determine the expected sequence of elements
    expected_elements_sequence = sequence[start_index: end_index + 1]
    units_in_elements = {element.element_unit for element in elements}
    final_elements: List[Union[TimeElement, str]] = []
    missing_units: List[str] = []
    for i, unit in enumerate(expected_elements_sequence):
        if unit in units_in_elements:
            element = get_element_by_unit_from_elements(unit, elements)
            assert element is not None, "element cannot be None (checked)"
            final_elements.append(element)
        else:
            final_elements.append(unit)
            missing_units.append(unit)
    return final_elements, missing_units


def are_ordered_elements_comparable(
    elements1: List[TimeElement], elements2: List[TimeElement]
) -> bool:
    """
    Determines if two lists of ordered time elements are matchable based
    on their sequence and scope.

    This function checks if the two lists of time elements, `elements1` and
    `elements2`, are ordered TimeElement
    object's list and have matchable sequences and scopes. The sequence of the
    elements is determined based on they follow the Gregorian or ISO format.
    The function ensures that both lists are ordered and match whether in terms
    of their last units and overall scope.

    Args:
        elements1 (List[TimeElement]): The first list of ordered time elements.
        elements2 (List[TimeElement]): The second list of ordered
                                        time elements.

    Returns:
        bool: Returns `True` if the ordered elements in both lists
                are matchable; `False` otherwise.

    Raises:
        ValueError: If `elements1` or `elements2` are not ordered,

    Example:
        >>> elements1 = [TimeElement('year', 2024), TimeElement('month', 8),
                            TimeElement('day', 13)]
        >>> elements2 = [TimeElement('year', 2024), TimeElement('month', 8),
                        TimeElement('day', 14)]
        >>> are_ordered_elements_matchable(elements1, elements2)
        True

        >>> elements1 = [TimeElement('year', 2024), TimeElement('month', 8)]
        >>> elements2 = [TimeElement('year', 2024), TimeElement('day', 13)]
        >>> are_ordered_elements_matchable(elements1, elements2)
        False

    """
    func_name = are_ordered_elements_comparable.__name__

    try:
        is_ordered_elements(elements1)
        is_ordered_elements(elements2)
    except ValueError as e:
        raise ValueError(f"{func_name}:arguments elements1 and elements2:{e}")
    else:
        elements1_sequence = get_elements_sequence(elements1)
        elements2_sequence = get_elements_sequence(elements2)
        assert elements1_sequence is not None, "Sequence1 not None (checked)"
        assert elements2_sequence is not None, "Sequence2 not None (checked)"
        elements1_last_unit_index = elements1_sequence.index(elements1[-1])
        elements2_last_unit_index = elements2_sequence.index(elements2[-1])

        scope1 = find_scope_in_ordered_elements(elements1)
        scope2 = find_scope_in_ordered_elements(elements2)

    return (scope1 == scope2
            and elements1_last_unit_index == elements2_last_unit_index)


def find_scope_in_ordered_elements(
        elements: List[TimeElement]) -> Optional[str]:
    """
    Finds the scope in a list of ordered elements.

    Args:
        elements (List[TimeElement]): A list of TimeElement objects.

    Returns:
        Optional [ str]:
            - str: The scope of the element which is the unit
                    before the first element of elements in the sequence,
            - None: If the list is empty or the first element is the
                    first in the sequence.
    """
    func_name = find_scope_in_ordered_elements.__name__
    try:
        is_ordered_elements(elements)
    except ValueError as e:
        raise ValueError(f"{func_name}:arguments elements:{e}")
    if not elements:
        return None
    sequence = get_elements_sequence(elements)
    assert sequence is not None, "Sequence cannot be None (prior check)"
    First_element_unit = elements[0].element_unit
    index = sequence.index(First_element_unit)
    if index == 0:
        return None
    else:
        return sequence[index - 1]


def check_elements_validity(elements: List[TimeElement]) -> bool:
    """
    Check the validity of the elements in a list.

    Args:
        elements (List[TimeElement]): The list of TimeElement objects to be checked.

    Returns:
        bool: True if all element has valid values according to each other values.

    Raises:
        ValueError: If any element is has valid.

    """
    # Rest of the code...
    func_name = check_elements_validity.__name__

    year, _ = get_value_by_unit_from_elements("YR", elements)
    month, _ = get_value_by_unit_from_elements("MH", elements)
    day, _ = get_value_by_unit_from_elements("DY", elements)
    week, _ = get_value_by_unit_from_elements("WK", elements)
    weekday, _ = get_value_by_unit_from_elements("WY", elements)

    if what_is_sequence(elements) == "gre":
        if day:
            if month:
                if day > TimeElement.get_max_value("DY", month):
                    ValueError(
                        f"{func_name}: The day value {day}"
                        f" is not valid for month {month}"
                    )
                else:
                    if (
                        year
                        and not calendar.isleap(year)
                        and month == 2
                        and day > 28
                    ):
                        raise ValueError(
                            f"{func_name}: The day value {day} is not valid"
                            f" for month {month} in non leap year {year}"
                        )
    elif what_is_sequence(elements) == "iso":
        if week == 53:
            possible, possible_years = (
                check_possibility_weekday_week(weekday, week))
            if not possible:
                # fmt: off
                raise ValueError(
                    f"{func_name}: The weekday {weekday}"
                    f"in week {week} is not valid"
                )
            # fmt: on
            else:
                if (year
                        and possible_years is not None
                        and year not in possible_years):
                    raise ValueError(
                        f"{func_name}: The year {year} does not have 53 weeks")
    elif what_is_sequence(elements) is None:
        raise ValueError(
            f"{func_name}: The elements are not in a valid sequence")
    return True


def is_valid_week_53(year: int) -> bool:
    """
    Check if a given year has 53 weeks.

    Parameters:
    year (int): The year to check.

    Returns:
    bool: True if the year has 53 weeks, False otherwise.
    """

    iso_year, week, weekday = datetime(year, 12, 28).isocalendar()
    return week == 53


def check_possibility_weekday_week(
    weekday: Union[TimeElement, int, None], week: Union[TimeElement, int]
) -> Tuple[bool, Optional[List[int]]]:
    """
    Check the possibility of a given weekday and week.

    Args:
        weekday (Union[TimeElement, int, None]): The weekday to check.
        week (Union[TimeElement, int]): The week to check.

    Returns:
        Tuple [ bool , Optional [ List [ int ] ] ]: A tuple containing:
                - A boolean indicates there are years with week and weekday
                in arguemnts
                - A list of years that have week(=53) and weekdays in the args.
                None means the week (<53) and weekday are exist in all years

    """

    if week != 53:
        return True, None
    else:
        possible_years = find_year_with_53_weeks(weekday)
        return bool(possible_years), possible_years


def find_ordered_elements_over_under_units(
    elements: List[TimeElement],
) -> Union[Dict[str, List[str]]]:

    """
        Finds the ordered elements over and under the given units.

        Args:
            elements (List[TimeElement]): A list of TimeElement objects
                representing the elements.

        Returns:
            Union [ Dict [ str, List [ str ]]] :
            - A dictionary containing two lists:
            - 'O' for elements over the given units.
            - 'U' for elements under the given units.
        Raises:
            ValueError: If the elements are not ordered.
        """
    func_name = find_ordered_elements_over_under_units.__name__
    try:
        is_ordered_elements(elements)
    except ValueError as e:
        raise ValueError(f"{func_name}:arguments elements:{e}")
    else:
        sequence = get_elements_sequence(elements)
        assert sequence is not None, "Sequence cannot be None (prior check)"
        elements_start_index = sequence.index(elements[0].element_unit)
        elements_end_index = sequence.index(elements[-1].element_unit)
        over_units = sequence[:elements_start_index]
        under_units = sequence[elements_end_index + 1:]
        over_and_under = {"O": list(over_units), "U": list(under_units)}
        return over_and_under


def iso_to_gregorian(
    year: int,
    week: int,
    weekday: int = 1,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> Optional[datetime]:
    """
    Convert ISO year, week, and weekday to Gregorian datetime.

    Args:
        year (int): The ISO year.
        week (int): The ISO week number.
        weekday (int, optional): The ISO weekday (1 for Monday, 7 for Sunday).
                                    Defaults to 1.
        hour (int, optional): The hour component of the resulting datetime.
                                    Defaults to 0.
        minute (int, optional): The minute component of the resulting datetime.
                                    Defaults to 0.
        second (int, optional): The second component of the resulting datetime.
                                    Defaults to 0.

    Returns:
        datetime: The corresponding Gregorian datetime or
                    None if inputs are invalid.
    """

    # Validate inputs
    if week < 1 or week > 53:
        return None
    if weekday < 1 or weekday > 7:
        return None
    if hour < 0 or hour > 23:
        return None
    if minute < 0 or minute > 59:
        return None
    if second < 0 or second > 59:
        return None

    # Calculate the first day of the ISO year
    first_day = datetime(year, 1, 4)  # Jan 4th is always in the first ISO week
    start_of_year = first_day - timedelta(days=first_day.isoweekday() - 1)

    # Calculate the date for the given week and weekday
    target_date = start_of_year + timedelta(weeks=week - 1, days=weekday - 1)

    # If the target week number is 53, check if the year actually has 53 weeks
    if week == 53 and target_date.year != year:
        return None

    # Add the time components
    final_date = target_date.replace(hour=hour, minute=minute, second=second)
    return final_date


# fmt : off
def complete_ordered_elements(
        elements: List[TimeElement]
) -> List[Union[int, str]]:
    # fmt : on

    """
    Constructs a complete ordered list of values based on a sequence of units,
    filling in values from the provided list of TimeElement instances and using
    placeholders for missing units.

    The function follows these rules:
    - For units present in the provided list, their corresponding values are used.
    - For units not present:
        - Units with a sequence index less than those in the provided list are filled
            with "O".
        - Units with a sequence index greater than those in the provided list are
            filled with "U".


    Args:
        elements (List[TimeElement]): An ordered list of TimeElement instances
        , each representing a unit and its value.

    The list is considered ordered if it meets the following criteria:
    - No duplicate units.
    - All units have valid values.
    - The list is sorted according to the expected sequence (ISO or Gregorian)

    Returns:
        List [ Union [ int , str ] ] : A complete ordered list of values,
                                    including "O" for units before those in the list
                                    and "U" for units after those in the list.

    Raises:
        ValueError: If the provided list of TimeElement instances is not
                    ordered.

    Example:
        - elements = [TimeElement(unit="day", value=15),
                        TimeElement(unit="month", value=8)]
        - result = complete_ordered_elements(elements)
        - result might be ["O", 8, 15, "U", "U", "U"] (depending on the sequence)



    """
    func_name = complete_ordered_elements.__name__

    try:
        is_ordered_elements(elements)
    except ValueError as e:
        raise ValueError(f"{func_name}: arguments elements: {e}")
    else:
        sequence = get_elements_sequence(elements)

        # Assert that sequence is not None, since it has been checked already
        assert sequence is not None, "Sequence cannot be None (prior check)"

        over_under_units = find_ordered_elements_over_under_units(elements)
        over_units = over_under_units["O"]
        under_units = over_under_units["U"]

        element_value_map = {
            el.element_unit: el.element_value for el in elements
        }

        values_list: List[Union[int, str]] = []
        # Iterate over the sequence to construct the ordered list
        for unit in sequence:
            if unit in over_units:
                values_list.append("O")
            elif unit in element_value_map:
                values_list.append(element_value_map[unit])
            elif unit in under_units:
                values_list.append("U")

        return values_list


# fmt: off
def compare_two_datetimes_ints(
        element_ints1: List[int], is_iso1: bool,
        element_ints2: List[int], is_iso2: bool) -> int:
    # fmt : on
    """
    Compare two datetimes represented as integers and return the result.

    Args:
        element_ints1 (tuple): A tuple representing the first
            datetime as integers.
        is_iso1 (bool): A boolean indicating whether the first
            datetime is in ISO format.
        element_ints2 (tuple): A tuple representing the second
            datetime as integers.
        is_iso2 (bool): A boolean indicating whether the second datetime is
                        in ISO format.

    Returns:
        int: 1 if the first datetime is greater than the second datetime,
            -1 if the first datetime is less than the second datetime,
            0 if the first datetime is equal to the second datetime.
    """

    dt1 = None
    dt2 = None

    if len(element_ints1) < 6 or len(element_ints2) < 6:
        return -2

    if is_iso1:
        dt1 = iso_to_gregorian(*element_ints1)
    else:
        year1, month1, day1, hour1, minute1, second1 = element_ints1[:6]
        dt1 = datetime(year1, month1, day1, hour1, minute1, second1)

    if is_iso2:
        dt2 = iso_to_gregorian(*element_ints2)
    else:
        year2, month2, day2, hour2, minute2, second2 = element_ints2[:6]
        dt2 = datetime(year2, month2, day2, hour2, minute2, second2)

    if dt1 is None or dt2 is None:
        return -2
    if dt1 > dt2:
        return 1
    elif dt1 < dt2:
        return -1
    else:
        return 0


# fmt: off
def compare_two_ordered_comparable_elements(
    elements1: List[TimeElement],
    elements2: List[TimeElement], leap_year: bool = False
) -> Union[int, Dict[str, List[int]]]:
    # fmt: on
    """
    Compare two lists of TimeElement objects and determine their relationship.

    Args:
        elements1 (List[TimeElement]): The first list of TimeElement objects.
        elements2 (List[TimeElement]): The second list of TimeElement objects.
        leap_year (bool, optional): Flag indicating whether to consider leap
                                    years. Defaults to False.

    Returns:
        Union [ int, Dict [ str, List [ int ] ] ]:
        - Dict : if comparison is possible in some years ( if the scope is
                year) and and
            one of the elements is iso has a week with 53 weeks, the function
            returns a dictionary contains "greater": years that
            elements1> elements2, "less" : elements1<elements2 and "equal" :
            elements1 = elements2.
        - int : for comparsion between two compelete datetime or or comparable
        elemnet in one year return: 1 if elements1 is greater than elements2,
        -1 if elements1 is less than elements2, 0 if elements1 is equal to
                elements2.
        - Note: if comparison is not possible in some years, the function
                returns -2.

    Raises:
        ValueError: If elements1 or elements2 are not valid or not comparable.

    """
    func_name = compare_two_ordered_comparable_elements.__name__

    try:
        if not are_ordered_elements_comparable(elements1, elements2):
            # fmt: off
            raise ValueError(
                f"{func_name}:elements1 and elements2 must be"
                f"ordered and matchable ot each other."
            )
            # fmt: on
    except ValueError as e:
        raise ValueError(f"{func_name}:arguments elements1 and elements2:{e}")

    else:
        is_leap_element1 = (True if (
            is_elements_leap(elements1) or leap_year) else False)
        is_leap_element2 = (True if (
            is_elements_leap(elements2) or leap_year) else False)
        compare_in_leap = is_leap_element1 or is_leap_element2 or leap_year

        is_iso_elements1 = (
            False if what_is_sequence(elements1) == "iso" else True
        )

        is_iso_elements2 = (
            False if what_is_sequence(elements2) == "iso" else True
        )
        compare_type: CompareSequnce
        if (is_iso_elements1 ^ is_iso_elements2):
            compare_type = CompareSequnce.ISO_GRE
        elif (is_iso_elements1 and is_iso_elements2):
            compare_type = CompareSequnce.ISO
        elif not is_iso_elements1 and not is_iso_elements2:
            compare_type = CompareSequnce.GRE

        complete_elements1 = complete_ordered_elements(elements1)
        complete_elements2 = complete_ordered_elements(elements2)

        compared_years: Dict[str, List[int]] = {
            "greater": [],
            "less": [],
            "equal": []
        }
        wk_value1, wk_value2, wy_value1, wy_value2 = None, None, None, None
        # set_years, temp_years = Optional[List[int]], Optional[List[int]]
        set_years = []
        temp_years = []
        wk_value1 = get_value_by_unit_from_elements("WK", elements1)
        wk_value2 = get_value_by_unit_from_elements("WK", elements2)
        wy_value1 = get_value_by_unit_from_elements("WY", elements1)
        wy_value2 = get_value_by_unit_from_elements("WY", elements2)
        if wk_value2 == 53 or wk_value2 == 53:
            iso_available_years = YEARS_WITH_53_WEEKS

        # Ensure that the values are of the correct type before passing
        if compare_type == CompareSequnce.GRE:
            if compare_in_leap:
                set_years = [2024]
            else:
                set_years = [2023]
        elif compare_type == CompareSequnce.ISO:
            set_years = list(iso_available_years) if iso_available_years else [2023]
        elif compare_type == CompareSequnce.ISO_GRE:
            if is_iso_elements1 and not is_iso_elements2:
                if is_iso_greg_compare_consistent(
                    3, 2023, wk_value1, wy_value1,  # type: ignore
                    2023, complete_elements2[1], complete_elements2[2]  # type: ignore
                ):
                    set_years = (
                        list(iso_available_years)
                        if iso_available_years else [2023]
                    )
                else:
                    temp_years = (
                        list(iso_available_years) if iso_available_years
                        else list(range(START_YEAR, END_YEAR + 1))
                    )
            elif not is_iso_elements1 and is_iso_elements2:
                if is_iso_greg_compare_consistent(
                    3, 2023, wk_value2, wy_value2,  # type: ignore
                    2023, complete_elements1[1], complete_elements1[2]  # type: ignore
                ):
                    set_years = [2023]
                else:
                    set_years = (
                        list(iso_available_years) if iso_available_years
                        else list(range(START_YEAR, END_YEAR + 1))
                    )
        set_years = [
            y for y in temp_years
            if (calendar.isleap(y) and compare_in_leap)
            ^ (not calendar.isleap(y) and not compare_in_leap)
        ]
        scope = find_scope_in_ordered_elements(elements1)
        if scope is None:
            set_elements1_ints = _set_complete_elements_values(
                complete_elements1, [1, 1, 1, 0, 0, 0]
            )
            set_elements2_ints = _set_complete_elements_values(
                complete_elements2, [1, 1, 1, 0, 0, 0]
            )
            return compare_two_datetimes_ints(
                set_elements1_ints,
                is_iso_elements1,
                set_elements2_ints,
                is_iso_elements2,
            )

        elif scope == "YR":
            if len(set_years) == 1:
                set_elements1_ints = _set_complete_elements_values(
                    complete_elements1, [set_years[0], 1, 1, 0, 0, 0]
                )
                set_elements2_ints = _set_complete_elements_values(
                    complete_elements2, [set_years[0], 1, 1, 0, 0, 0]
                )
                return compare_two_datetimes_ints(
                    set_elements1_ints,
                    is_iso_elements1,
                    set_elements2_ints,
                    is_iso_elements2,
                )
            else:
                for year in set_years:
                    set_elements1_ints = _set_complete_elements_values(
                        complete_elements1, [year, 1, 1, 0, 0, 0]
                    )
                    set_elements2_ints = _set_complete_elements_values(
                        complete_elements2, [year, 1, 1, 0, 0, 0]
                    )
                    result = compare_two_datetimes_ints(
                        set_elements1_ints,
                        is_iso_elements1,
                        set_elements2_ints,
                        is_iso_elements2,
                    )
                    if result == 1:
                        compared_years["greater"].append(year)
                    elif result == -1:
                        compared_years["less"].append(year)
                    else:
                        compared_years["equal"].append(year)
                return compared_years
        else:
            for x, y in zip(elements1, elements2):
                if x.element_value > y.element_value:
                    return 1
                elif x.element_value < y.element_value:
                    return -1
        return 0


def units_vlaues_to_ordered_elements(
    year: Optional[int],
    month: Optional[int],
    day: Optional[int],
    hour: Optional[int],
    minute: Optional[int],
    second: Optional[int],
    weekday: Optional[int],
    week: Optional[int],
) -> List[TimeElement]:
    """
    Convert units values to ordered elements.

    Args:
        year (Optional[int ]): The year value.
        month (Optional[int ]): The month value.
        day (Optional[int ]): The day value.
        hour (Optional[int ]): The hour value.
        minute (Optional[int ]): The minute value.
        second (Optional[int ]): The second value.
        weekday (Optional[int ]): The weekday value.
        week (Optional[int ]): The week value.

    Returns:
        List[TimeElement]: The list of ordered TimeElement objects.

    Raises:
        ValueError: If the result elements are not ordered.

    """

    func_name = units_vlaues_to_ordered_elements.__name__
    arguments = [
        ("year", year),
        ("month", month),
        ("day", day),
        ("hour", hour),
        ("minute", minute),
        ("second", second),
        ("weekday", weekday),
        ("week", week),
    ]

    temp_elements = [
        TimeElement(unit, value)
        for unit, value in arguments
        if value is not None
    ]

    final_list, _ = sort_elements_by_sequence(temp_elements)

    if not final_list or final_list is None:
        return []
    else:
        # Filter out any strings, ensuring only TimeElement objects remain
        filtered_final_list = [el for el in final_list if isinstance(
            el, TimeElement)]

        try:
            is_ordered_elements(temp_elements)
        except ValueError as e:
            raise ValueError(f"{func_name}:result elements:{e}")
        else:
            return filtered_final_list


def ordered_elements_default_representation(
        elements: List[TimeElement]) -> str:
    """
    Returns the default representation of ordered elements.

    Args:
        elements (List[TimeElement]): A list of TimeElement objects.

    Returns:
        str: The default representation of the ordered elements.

    Raises:
        ValueError: If the elements are not ordered.

    """

    func_name = ordered_elements_default_representation.__name__

    try:
        is_ordered_elements(elements)
    except ValueError as e:
        raise ValueError(f"{func_name}:arguments elements:{e}")
    else:
        repres = [el.default_representation for el in elements]
        return "".join(repres)


def ordered_elements_alternative_representation(
        elements: List[TimeElement]) -> str:
    method_name = ordered_elements_alternative_representation.__name__

    try:
        is_ordered_elements(elements)
    except ValueError as e:
        raise ValueError(f"{method_name}:arguments elements:{e}")
    else:
        repres = [el.alternative_representation for el in elements]
        return "".join(repres)


def can_contains(container: List[TimeElement], contained: List[TimeElement]) -> bool:

    func_name = can_contains.__name__

    if not container or not contained:
        return False
    try:
        is_ordered_elements(container) and is_ordered_elements(contained)
    except ValueError as e:
        raise ValueError(f"{func_name}:arguments :{e}")
    else:
        container_seq_name = what_is_sequence(container)
        contained_seq_name = what_is_sequence(contained)
        if container_seq_name is None or contained_seq_name is None:
            return False
        if container_seq_name != contained_seq_name:
            return False
        container_unders = find_ordered_elements_over_under_units(container)["U"]
        contained_units = [el.element_unit for el in contained]
        if not all(unit in container_unders for unit in contained_units):
            return False
        else:
            return True
