# Advanced Time Handling Library for Python (In Development)

## Overview
This project aims to develop an advanced time-handling library for Python, offering a higher level of control over time units, time sequences (ISO and Gregorian), and complex time span manipulations. The library is designed to provide flexibility in dealing with complex scheduling, calendaring, and period-based operations that standard libraries don't fully address.

🚧 **Project Status:** In Development  
This project is currently under active development and is not yet complete. Many of the key features mentioned below are still being worked on, and future updates will include additional functionality, improvements, and documentation.

## Planned Key Features
The following features are planned for the completed version of this library:

- **Time Units and Elements**: Work with detailed time units such as seconds (SD), minutes (ME), hours (HR), days (DY), weeks (WK), months (MH), and years (YR), with full control over time element values.
- **Time Scopes and Sequences**: Support for managing different time sequences (ISO and Gregorian) and handling leap years and months with varying lengths.
- **Partial Date-Time Support**: Ability to work with time points that are not complete ISO or Gregorian date-times, such as `Aug21T22` or week-based representations like `W43SU` (Week 43, Sunday) and `W45MO` (Week 45, Monday), allowing for highly customizable time-point precision.
- **Over and Under Units**: Advanced time point control by defining over and under units for precise time span management.
- **TimePoint and TimeSpan**: Create individual time points and spans that support detailed calculations, period-based comparisons, and sequence-specific behavior.
- **Period Occurrence Calculation**: Enable complex period comparisons and occurrences across different calendar systems.
- **Customizable Representations**: Flexible string representations for time points and spans, suitable for various use cases.

## Why This Project?
While Python offers standard libraries such as `datetime` and third-party solutions like `pendulum`, they often lack fine-grained control over time sequences and complex spans. This project aims to bridge that gap by:

1. **Supporting Mixed Time Sequences**: Allowing for operations across both ISO and Gregorian time systems in a single unified framework.
2. **Granular Time Control**: Providing unmatched precision in defining and manipulating time units and periods.
3. **Handling Complex Spans**: Offering easy ways to compute occurrences, overlaps, and comparisons for spans in different time scopes.

## Comparison to Existing Libraries
The goal of this library is to extend the functionality of existing libraries like `datetime`, `arrow`, and `pendulum`. While these libraries are great for general-purpose date and time handling, this project will offer:

- **Complex Scope Management**: Allowing you to define and work with time scopes in a way that existing libraries don’t.
- **Detailed Element Handling**: Managing individual time units and their relationships with over/under units for granular control.
- **Advanced Span Calculations**: Simplifying complex calendar computations, especially when dealing with spans of time across leap years, overlapping periods, or different time formats.

## License
This project is licensed under the Apache-2.0 License. See the LICENSE file for more details.
