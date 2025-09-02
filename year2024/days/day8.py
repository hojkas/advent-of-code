from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from helpers import InputLoader
from lib.abstract_day import AbstractDay
from lib.models import GenericMapField, GenericMapRepresentationDeprecated


class FieldType(Enum):
    EMPTY = 0
    ANTENNA = 1


@dataclass
class TerrainField(GenericMapField):
    type: FieldType
    antenna_name: Optional[str] = None


@dataclass
class AntennaGroup:
    name: str
    terrain_map: 'TerrainMap'
    positions: list[TerrainField] = field(default_factory=list)
    antinodes: list[TerrainField] = field(default_factory=list)

    def calculate_basic_antinodes(self) -> None:
        potential_antinodes = self._get_potential_basic_antinode_coordinates()
        for potential_row, potential_col in potential_antinodes:
            if self.terrain_map.coordinates_within_bounds(potential_row, potential_col):
                self.antinodes.append(self.terrain_map.fields[potential_row][potential_col])

    def _get_potential_basic_antinode_coordinates(self) -> list[tuple[int, int]]:
        coordinates = set()
        for antenna_id, first_antenna in enumerate(self.positions[:-1]):
            for second_antenna in self.positions[antenna_id + 1:]:
                first_coordinate, second_coordinate = self._compute_possible_basic_antinodes_for_pair(
                    first_antenna, second_antenna
                )
                coordinates.add(first_coordinate)
                coordinates.add(second_coordinate)
        return list(coordinates)

    @staticmethod
    def _compute_possible_basic_antinodes_for_pair(
        first: TerrainField, second: TerrainField
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        first_to_second_row_diff = second.row - first.row
        first_to_second_col_diff = second.col - first.col
        coordinate_after_second_item = (second.row + first_to_second_row_diff, second.col + first_to_second_col_diff)
        coordinate_before_first_item = (first.row - first_to_second_row_diff, first.col - first_to_second_col_diff)
        return coordinate_before_first_item, coordinate_after_second_item

    def calculate_advanced_antinodes(self) -> None:
        potential_antinodes = self._get_potential_advanced_antinode_coordinates()
        for potential_row, potential_col in potential_antinodes:
            self.antinodes.append(self.terrain_map.fields[potential_row][potential_col])

    def _get_potential_advanced_antinode_coordinates(self) -> list[tuple[int, int]]:
        coordinates = set()
        for antenna_id, first_antenna in enumerate(self.positions[:-1]):
            for second_antenna in self.positions[antenna_id + 1:]:
                coordinates.update(
                    self._compute_possible_advanced_antinode_coordinates_for_a_pair(first_antenna, second_antenna)
                )
        return list(coordinates)

    def _compute_possible_advanced_antinode_coordinates_for_a_pair(
        self, first: TerrainField, second: TerrainField
    ) -> list[tuple[int, int]]:
        row_diff = second.row - first.row
        col_diff = second.col - first.col
        # first one needs to be explicitly added, second will be hit in one direction section
        coordinates = [(first.row, first.col)]

        # one direction
        current_row = first.row + row_diff
        current_col = first.col + col_diff
        while self.terrain_map.coordinates_within_bounds(current_row, current_col):
            coordinates.append((current_row, current_col))
            current_row += row_diff
            current_col += col_diff

        # other direction
        current_row = first.row - row_diff
        current_col = first.col - col_diff
        while self.terrain_map.coordinates_within_bounds(current_row, current_col):
            coordinates.append((current_row, current_col))
            current_row -= row_diff
            current_col -= col_diff

        return coordinates


@dataclass
class TerrainMap(GenericMapRepresentationDeprecated):
    fields: list[list[TerrainField]]  # to retype for type hints
    antenna_groups: dict[str, AntennaGroup] = field(default_factory=dict)

    def __init__(self, fields: list[list[TerrainField]]) -> None:
        super().__init__(fields)
        self.antenna_groups = {}
        for field_row in self.fields:
            for field_item in field_row:
                if field_item.type == FieldType.EMPTY:
                    continue
                if field_item.antenna_name not in self.antenna_groups:
                    antenna_group = AntennaGroup(name=field_item.antenna_name, terrain_map=self)
                    antenna_group.positions.append(field_item)
                    self.antenna_groups[field_item.antenna_name] = antenna_group
                else:
                    self.antenna_groups[field_item.antenna_name].positions.append(field_item)


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        terrain_map = parse_terrain_map(self.input_loader.load_input_array("\n"))
        unique_antinodes = set()
        for antenna_group in terrain_map.antenna_groups.values():
            antenna_group.calculate_basic_antinodes()
            for antinode in antenna_group.antinodes:
                unique_antinodes.add((antinode.row, antinode.col))
        return len(unique_antinodes)

    def run_part_two(self):
        terrain_map = parse_terrain_map(self.input_loader.load_input_array("\n"))
        unique_antinodes = set()
        for antenna_group in terrain_map.antenna_groups.values():
            antenna_group.calculate_advanced_antinodes()
            for antinode in antenna_group.antinodes:
                unique_antinodes.add((antinode.row, antinode.col))
        return len(unique_antinodes)


def parse_terrain_map(raw_terrain_map: list[str]) -> TerrainMap:
    field_map = []
    for row_id, raw_line in enumerate(raw_terrain_map):
        field_line = []
        for col_id, char in enumerate(raw_line):
            if char == ".":
                field_line.append(TerrainField(row=row_id, col=col_id, type=FieldType.EMPTY))
            else:
                field_line.append(TerrainField(row=row_id, col=col_id, type=FieldType.ANTENNA, antenna_name=char))
        field_map.append(field_line)

    return TerrainMap(field_map)
