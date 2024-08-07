from dataclasses import dataclass, field
from typing import Optional

from lib.abstract_day import AbstractDay
from helpers import InputLoader


@dataclass
class UniverseRow:
    id: int
    galaxies: list['Galaxy'] = field(default_factory=list)

    @property
    def empty(self) -> bool:
        return len(self.galaxies) == 0


@dataclass
class UniverseColumn:
    id: int
    galaxies: list['Galaxy'] = field(default_factory=list)

    @property
    def empty(self) -> bool:
        return len(self.galaxies) == 0


@dataclass
class Galaxy:
    id: int
    row_id: int
    column_id: int


class Universe:
    def __init__(self, input_lines: list[str]) -> None:
        self.galaxies = []
        self.rows = [UniverseRow(i) for i in range(len(input_lines))]
        self.columns = [UniverseColumn(i) for i in range(len(input_lines[0]))]

        galaxy_id = 0
        for row_id, line in enumerate(input_lines):
            for col_id, char in enumerate(line):
                if char == "#":
                    galaxy = Galaxy(galaxy_id, row_id, col_id)
                    galaxy_id += 1
                    self.galaxies.append(galaxy)
                    self.rows[row_id].galaxies.append(galaxy)
                    self.columns[col_id].galaxies.append(galaxy)
                elif char != ".":
                    raise RuntimeError(f"Unexpected char {char}")

    def count_distance(self, first_galaxy: Galaxy, second_galaxy: Galaxy, empty_space_expansion: int = 2) -> int:
        min_col_id = first_galaxy.column_id
        max_col_id = second_galaxy.column_id
        if min_col_id > max_col_id:
            min_col_id, max_col_id = max_col_id, min_col_id

        min_row_id = first_galaxy.row_id
        max_row_id = second_galaxy.row_id
        if min_row_id > max_row_id:
            min_row_id, max_row_id = max_row_id, min_row_id

        column_adjustment = 0
        for column in self.columns[min_col_id + 1:max_col_id]:
            if column.empty:
                column_adjustment += (empty_space_expansion - 1)  # to account for the col still counted bellow

        row_adjustment = 0
        for row in self.rows[min_row_id + 1:max_row_id]:
            if row.empty:
                row_adjustment += (empty_space_expansion - 1)  # to account for the row still counted bellow

        return max_col_id - min_col_id + column_adjustment + max_row_id - min_row_id + row_adjustment


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_lines = self.input_loader.load_input_array(item_separator="\n")
        universe = Universe(input_lines)
        result = part_one(universe)
        return result

    def run_part_two(self):
        input_lines = self.input_loader.load_input_array(item_separator="\n")
        universe = Universe(input_lines)
        result = part_two(universe)
        return result


def part_one(universe: Universe) -> int:
    total_distance = 0
    for i, galaxy in enumerate(universe.galaxies):
        for another_galaxy in universe.galaxies[i+1:]:
            total_distance += universe.count_distance(galaxy, another_galaxy)
    return total_distance


def part_two(universe: Universe) -> int:
    total_distance = 0
    for i, galaxy in enumerate(universe.galaxies):
        for another_galaxy in universe.galaxies[i+1:]:
            total_distance += universe.count_distance(galaxy, another_galaxy, 1000000)
    return total_distance
