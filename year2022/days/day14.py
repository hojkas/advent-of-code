from enum import Enum
from typing import Union

from lib.abstract_day import AbstractDay
from helpers.input_loader import InputLoader


class CaveFieldType(Enum):
    EMPTY = 0,
    ROCK = 1,
    SAND = 2


def coordinates_from_point_string(point_string):
    string_split = point_string.split(",")
    return int(string_split[0]), int(string_split[1])


class CaveMap:
    def __init__(self, rock_formations: list[list[str]]):
        self.known_map_fields = {}
        for rock_formation in rock_formations:
            self._mark_rock_formation(rock_formation)
        self.max_depth = max([key for inner_dict in self.known_map_fields.values() for key in inner_dict.keys()])


    def _mark_rock_formation(self, rock_formation: list[str]):
        last_point_col, last_point_depth = coordinates_from_point_string(rock_formation[0])

        for point_string in rock_formation[1:]:
            point_col, point_depth = coordinates_from_point_string(point_string)

            if point_depth == last_point_depth:
                self._mark_horizontal_rock_line(last_point_col, point_col, point_depth)
            elif point_col == last_point_col:
                self._mark_vertical_rock_line(last_point_depth, point_depth, point_col)
            else:
                raise RuntimeError("Expected rock formations to be lines with diff only in col or depth")

            last_point_col, last_point_depth = point_col, point_depth

    def _mark_horizontal_rock_line(self, start_col, end_col, depth):
        lower_col = start_col if start_col < end_col else end_col
        higher_col = end_col if start_col < end_col else start_col

        for col in range(lower_col, higher_col + 1):
            self.mark_map_field(CaveFieldType.ROCK, col, depth)

    def _mark_vertical_rock_line(self, start_depth, end_depth, col):
        lower_depth_value = start_depth if start_depth < end_depth else end_depth
        higher_depth_value = end_depth if start_depth < end_depth else start_depth

        for depth in range(lower_depth_value, higher_depth_value + 1):
            self.mark_map_field(CaveFieldType.ROCK, col, depth)

    def mark_map_field(self, field_type: CaveFieldType, col, depth) -> None:
        if col not in self.known_map_fields.keys():
            self.known_map_fields[col] = {depth: field_type}
        else:
            self.known_map_fields[col][depth] = field_type

    def fetch_map_field(self, col, depth) -> CaveFieldType:
        if col not in self.known_map_fields.keys():
            return CaveFieldType.EMPTY
        if depth not in self.known_map_fields[col].keys():
            return CaveFieldType.EMPTY
        return self.known_map_fields[col][depth]


class SandGrain:
    def __init__(self, col, depth):
        self.col = col
        self.depth = depth


class SandSimulation:
    def __init__(self, cave_map, spawn_col=500, spawn_depth=0, infinite_floor=False):
        self.stable_sand_grains = 0
        self.cave_map: CaveMap = cave_map
        self.spawn_col = spawn_col
        self.spawn_depth = spawn_depth
        self.infinite_floor = infinite_floor

    def run(self):
        while True:
            if self.cave_map.fetch_map_field(self.spawn_col, self.spawn_depth) == CaveFieldType.SAND:
                return
            grain_landed = self._simulate_one_grain()
            if not grain_landed:
                return

    def _simulate_one_grain(self) -> bool:
        grain = SandGrain(self.spawn_col, self.spawn_depth)
        while True:
            can_move = self._one_grain_move(grain)
            if not can_move:
                self.stable_sand_grains += 1
                self.cave_map.mark_map_field(CaveFieldType.SAND, grain.col, grain.depth)
                return True
            if not self.infinite_floor and grain.depth > self.cave_map.max_depth:
                return False

    def _one_grain_move(self, grain) -> bool:
        if grain.depth == self.cave_map.max_depth + 1:
            return False

        if self.cave_map.fetch_map_field(grain.col, grain.depth + 1) == CaveFieldType.EMPTY:
            grain.depth += 1
            return True

        if self.cave_map.fetch_map_field(grain.col - 1, grain.depth + 1) == CaveFieldType.EMPTY:
            grain.col -= 1
            grain.depth += 1
            return True

        if self.cave_map.fetch_map_field(grain.col + 1, grain.depth + 1) == CaveFieldType.EMPTY:
            grain.col += 1
            grain.depth += 1
            return True

        return False


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        rock_formation = self.input_loader.load_input_array_of_array(subarray_separator="\n", item_separator=" -> ")
        cave_map = CaveMap(rock_formation)
        sand_simulation = SandSimulation(cave_map)
        sand_simulation.run()
        return sand_simulation.stable_sand_grains

    def run_part_two(self):
        rock_formation = self.input_loader.load_input_array_of_array(subarray_separator="\n", item_separator=" -> ")
        cave_map = CaveMap(rock_formation)
        sand_simulation = SandSimulation(cave_map, infinite_floor=True)
        sand_simulation.run()
        return sand_simulation.stable_sand_grains
