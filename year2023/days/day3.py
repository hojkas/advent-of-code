from typing import Union
from dataclasses import dataclass, field

from lib.abstract_day import AbstractDay
from helpers import InputLoader


@dataclass
class Part:
    value: int
    row: int
    column_start: int
    column_end: int
    machine_part: bool = False
    surrounding_locations: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class Symbol:
    representation: str
    row: int
    column: int
    is_gear: bool = False
    gear_ratio: int = 0


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_field = self.input_loader.load_input_array(item_separator="\n")
        symbols = load_symbols(input_field)
        parts = load_parts(input_field)
        determine_true_machine_parts(parts, symbols)
        result = sum([part.value for part in parts if part.machine_part])
        return result

    def run_part_two(self):
        input_field = self.input_loader.load_input_array(item_separator="\n")
        symbols = load_symbols(input_field)
        parts = load_parts(input_field)
        determine_true_gears(parts, symbols)
        result = sum([symbol.gear_ratio for symbol in symbols if symbol.is_gear])
        return result


def load_symbols(input_field: list[str]) -> list[Symbol]:
    symbols = []
    for row, line in enumerate(input_field):
        for col, char in enumerate(line):
            if not char.isdigit() and char != ".":
                symbols.append(Symbol(representation=char, row=row, column=col))
    return symbols


def load_parts(input_field: list[str]) -> list[Part]:
    parts = []
    for row, line in enumerate(input_field):
        part_in_progress = None
        part_column_start = None
        for col, char in enumerate(line):
            if char.isdigit():
                if part_in_progress:
                    part_in_progress += char
                else:
                    part_in_progress = char
                    part_column_start = col
            else:
                if part_in_progress:
                    parts.append(Part(
                        value=int(part_in_progress),
                        row=row,
                        column_start=part_column_start,
                        column_end=col - 1
                    ))
                    part_in_progress = None
        if part_in_progress:
            parts.append(Part(
                value=int(part_in_progress),
                row=row,
                column_start=part_column_start,
                column_end=len(line) - 1
            ))

    for part in parts:
        # add locations on the same row
        part.surrounding_locations = [
            (part.row, part.column_start - 1),
            (part.row, part.column_end + 1)
        ]
        # add locations on the row above and below
        for col in range(part.column_start - 1, part.column_end + 2):
            part.surrounding_locations.append((part.row - 1, col))
            part.surrounding_locations.append((part.row + 1, col))

    return parts


def determine_true_machine_parts(parts: list[Part], symbols: list[Symbol]) -> None:
    for part in parts:
        determine_true_machine_part(part, symbols)


def determine_true_machine_part(part: Part, symbols: list[Symbol]) -> None:
    for symbol in symbols:
        if (symbol.row, symbol.column) in part.surrounding_locations:
            part.machine_part = True
            return


def determine_true_gears(parts: list[Part], symbols: list[Symbol]) -> None:
    for symbol in symbols:
        if symbol.representation == "*":
            determine_true_gear(parts, symbol)


def determine_true_gear(parts: list[Part], symbol: Symbol) -> None:
    adjacent_parts = []
    symbol_location = (symbol.row, symbol.column)
    for part in parts:
        if symbol_location in part.surrounding_locations:
            adjacent_parts.append(part)

    if len(adjacent_parts) == 2:
        symbol.is_gear = True
        symbol.gear_ratio = adjacent_parts[0].value * adjacent_parts[1].value
