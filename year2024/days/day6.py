from enum import Enum
from typing import Optional

from lib.abstract_day import AbstractDay
from helpers import InputLoader, Direction
from lib.exceptions import RunException


class OutOfBoundsError(RunException):
    pass


class ObstacleEncounteredError(RunException):
    pass


class FieldType(Enum):
    EMPTY = "."
    OBSTACLE = "#"
    GUARD_UP = "^"


class Field:
    def __init__(self, field_type: FieldType, row: int, col: int):
        self.type = field_type
        self.visited = True if field_type == FieldType.GUARD_UP else False
        self.row = row
        self.col = col


class LabMap:
    def __init__(self, string_map: list[str]) -> None:
        self.fields = []
        self.current_guard_field = None

        for row_id, line in enumerate(string_map):
            map_line = []
            for col_id, char in enumerate(line):
                if char == FieldType.EMPTY.value:
                    map_line.append(Field(FieldType.EMPTY, row_id, col_id))
                elif char == FieldType.OBSTACLE.value:
                    map_line.append(Field(FieldType.OBSTACLE, row_id, col_id))
                elif char == FieldType.GUARD_UP.value:
                    self.current_guard_field = Field(FieldType.GUARD_UP, row_id, col_id)
                    self.current_guard_direction = Direction.UP
                    map_line.append(self.current_guard_field)
                else:
                    raise RunException(f"Unknown field value: {char}")
            self.fields.append(map_line)

        self.row_count = len(self.fields)
        self.col_count = len(self.fields[0])

    @property
    def fields_visited_count(self) -> int:
        return sum(1 for line in self.fields for field in line if field.visited)

    def _coordinates_within_bounds(self, row, col):
        return 0 <= row < self.row_count and 0 <= col < self.col_count

    def get_next_field_in_direction(self, field: Field, direction: Direction) -> Field:
        new_row = field.row + direction.value[0]
        new_col = field.col + direction.value[1]
        if not self._coordinates_within_bounds(new_row, new_col):
            raise OutOfBoundsError()
        new_field = self.fields[new_row][new_col]
        if new_field.type == FieldType.OBSTACLE:
            raise ObstacleEncounteredError()
        return new_field


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        map_array = self.input_loader.load_input_array(item_separator="\n")
        lab_map = LabMap(map_array)
        simulate_guard_movement(lab_map)
        return lab_map.fields_visited_count

    def run_part_two(self):
        return "---"


def simulate_guard_movement(lab_map: LabMap) -> None:
    try:
        while True:
            move_guard_one_step(lab_map)
    except OutOfBoundsError:
        return


def move_guard_one_step(lab_map: LabMap) -> None:
    while True:
        try:
            next_field = lab_map.get_next_field_in_direction(
                field=lab_map.current_guard_field, direction=lab_map.current_guard_direction
            )
            break
        except ObstacleEncounteredError:
            lab_map.current_guard_direction = lab_map.current_guard_direction.next_clockwise_cardinal

    next_field.visited = True
    lab_map.current_guard_field = next_field
