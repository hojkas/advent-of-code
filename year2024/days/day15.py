from dataclasses import dataclass
from enum import StrEnum
from typing import cast, Literal

from helpers import InputLoader
from lib.abstract_day import AbstractDay
from lib.models import Direction, GenericMapField, GenericMapRepresentationDeprecated


class NoMoreInstructions(Exception):
    """
    No more instructions available.
    """


class FieldType(StrEnum):
    WALL = "#"
    EMPTY = "."
    CRATE = "O"
    CRATE_LEFT = "["
    CRATE_RIGHT = "]"


@dataclass
class Robot(GenericMapField):
    pass


@dataclass
class InstructionSet:
    instructions: list[Direction]
    current_index: int = 0

    def next_instruction(self) -> Direction | None:
        if self.current_index >= len(self.instructions):
            return None

        instruction = self.instructions[self.current_index]
        self.current_index += 1
        return instruction


@dataclass
class FactoryMapField(GenericMapField):
    type: FieldType

    @property
    def gps_coordiates(self) -> int:
        return self.row * 100 + self.col

    def __hash__(self) -> int:
        return hash(self.gps_coordiates)


@dataclass
class FactoryMap(GenericMapRepresentationDeprecated):
    fields: list[list[FactoryMapField]]
    instructions: InstructionSet
    robot: Robot

    @property
    def crate_gps_coordinates(self) -> int:
        gps_sum = 0
        for row in self.fields:
            for field in row:
                if field.type in (FieldType.CRATE, FieldType.CRATE_LEFT):
                    gps_sum += field.gps_coordiates
        return gps_sum

    def print_map(self):
        for row in self.fields:
            for field in row:
                if field.row == self.robot.row and field.col == self.robot.col:
                    print("@", end="")
                else:
                    print(field.type.value, end="")
            print()

    def process_next_instruction(self, wide_version: bool) -> bool:
        instruction = self.instructions.next_instruction()
        if instruction is None:
            return False

        if self.robot_can_move(instruction, wide_version):
            self.move_robot(instruction, wide_version)
        return True

    def _robot_can_move_narrow_version(self, direction: Direction) -> bool:
        current_field = self.robot
        while True:
            next_field = cast(FactoryMapField, self.get_next_field_in_direction(current_field, direction))
            if next_field.type == FieldType.WALL:
                return False
            if next_field.type == FieldType.EMPTY:
                return True
            current_field = next_field

    def _check_move_and_gather_movable_crates(
            self, direction: Literal[Direction.UP, Direction.DOWN], gather_crates: bool
    ) -> tuple[bool, set[FactoryMapField] | None]:
        next_field = cast(FactoryMapField, self.get_next_field_in_direction(self.robot, direction))
        crates_to_move = set() if gather_crates else None
        to_investigate = set()

        if next_field.type == FieldType.WALL:
            return False, crates_to_move
        elif next_field.type == FieldType.EMPTY:
            return True, crates_to_move
        elif next_field.type in (FieldType.CRATE_LEFT, FieldType.CRATE_RIGHT):
            to_investigate.add(next_field)
            to_investigate.add(self.get_other_crate_part(next_field))
            if crates_to_move is not None:
                crates_to_move.add(next_field)
                crates_to_move.add(self.get_other_crate_part(next_field))
        else:
            raise RuntimeError(f"Unknown field type for wide version: {next_field.type}")

        while len(to_investigate) > 0:
            current_field = to_investigate.pop()
            next_field = cast(FactoryMapField, self.get_next_field_in_direction(current_field, direction))
            if next_field.type == FieldType.WALL:
                return False, crates_to_move
            elif next_field.type == FieldType.EMPTY:
                continue
            elif next_field.type in (FieldType.CRATE_LEFT, FieldType.CRATE_RIGHT):
                to_investigate.add(next_field)
                to_investigate.add(self.get_other_crate_part(next_field))
                if crates_to_move is not None:
                    crates_to_move.add(next_field)
                    crates_to_move.add(self.get_other_crate_part(next_field))
            else:
                raise RuntimeError(f"Unknown field type for wide version: {next_field.type}")

        return True, crates_to_move

    def _robot_can_move_wide_version_vertical(self, direction: Literal[Direction.UP, Direction.DOWN]) -> bool:
        can_move, _ = self._check_move_and_gather_movable_crates(direction, gather_crates=False)
        return can_move

    def _robot_can_move_wide_version(self, direction: Direction) -> bool:
        if direction in (Direction.LEFT, Direction.RIGHT):
            return self._robot_can_move_narrow_version(direction)
        elif direction in (Direction.UP, Direction.DOWN):
            return self._robot_can_move_wide_version_vertical(direction)
        else:
            raise RuntimeError(f"Unknown direction {direction}")

    def robot_can_move(self, direction: Direction, wide_version: bool) -> bool:
        if wide_version:
            return self._robot_can_move_wide_version(direction)
        else:
            return self._robot_can_move_narrow_version(direction)

    def _create_mapping_after_crate_move(
        self, creates_to_move: set[FactoryMapField], direction: Direction
    ) -> dict[FactoryMapField, FieldType]:
        mapping = {}

        # put empty for now in all the previous fields
        for create_piece in creates_to_move:
            mapping[create_piece] = FieldType.EMPTY

        # for each create piece, mark it for moving in the direction
        for create_piece in creates_to_move:
            field_in_move_direction = cast(FactoryMapField, self.get_next_field_in_direction(create_piece, direction))
            mapping[field_in_move_direction] = create_piece.type

        return mapping

    def _move_robot_narrow_version(self, direction: Direction):
        next_field_to_resolve = self.get_next_field_in_direction(self.robot, direction)
        self.robot.row += direction.value[0]
        self.robot.col += direction.value[1]

        if next_field_to_resolve.type == FieldType.EMPTY:
            return
        else:
            next_field_to_resolve.type = FieldType.EMPTY  # set empty as robot pushed it out

        while True:
            next_field_to_resolve = self.get_next_field_in_direction(next_field_to_resolve, direction)
            if next_field_to_resolve.type == FieldType.EMPTY:
                next_field_to_resolve.type = FieldType.CRATE
                return

    def _move_robot_wide_version_horizontal(self, direction: Literal[Direction.LEFT, Direction.RIGHT]) -> None:
        next_field_to_resolve = self.get_next_field_in_direction(self.robot, direction)
        self.robot.row += direction.value[0]
        self.robot.col += direction.value[1]

        if next_field_to_resolve.type == FieldType.EMPTY:
            return

        crate_piece_getting_pushed = next_field_to_resolve.type
        next_field_to_resolve.type = FieldType.EMPTY  # set empty as robot pushed it out

        while True:
            next_field_to_resolve = self.get_next_field_in_direction(next_field_to_resolve, direction)
            if next_field_to_resolve.type == FieldType.EMPTY:
                next_field_to_resolve.type = crate_piece_getting_pushed
                return
            crate_piece_to_place = crate_piece_getting_pushed
            crate_piece_getting_pushed = next_field_to_resolve.type
            next_field_to_resolve.type = crate_piece_to_place


    def _move_robot_wide_version_vertical(self, direction: Literal[Direction.UP, Direction.DOWN]) -> None:
        crates_to_move = self._check_move_and_gather_movable_crates(direction, gather_crates=True)[1]
        field_states_after_move = self._create_mapping_after_crate_move(crates_to_move, direction)
        for field, type_after_move in field_states_after_move.items():
            field.type = type_after_move
        self.robot.row += direction.value[0]
        self.robot.col += direction.value[1]

    def _move_robot_wide_version(self, direction: Direction) -> None:
        if direction in (Direction.LEFT, Direction.RIGHT):
            self._move_robot_wide_version_horizontal(direction)
        elif direction in (Direction.UP, Direction.DOWN):
            self._move_robot_wide_version_vertical(direction)
        else:
            raise RuntimeError(f"Unknown instruction {direction}")

    def move_robot(self, direction: Direction, wide_version: bool) -> None:
        if wide_version:
            self._move_robot_wide_version(direction)
        else:
            self._move_robot_narrow_version(direction)

    def get_other_crate_part(self, crate_field: FactoryMapField) -> FactoryMapField:
        if crate_field.type == FieldType.CRATE_RIGHT:
            return cast(FactoryMapField, self.get_next_field_in_direction(crate_field, Direction.LEFT))
        elif crate_field.type == FieldType.CRATE_LEFT:
            return cast(FactoryMapField, self.get_next_field_in_direction(crate_field, Direction.RIGHT))
        else:
            raise RuntimeError("Get other crate part called on non crate field!")


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: InputLoader | None = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        raw_map, raw_instructions = self.input_loader.load_input_array("\n\n")
        factory_map = parse_factory_map(raw_map, parse_instructions(raw_instructions))

        while factory_map.process_next_instruction(wide_version=False):
            # returns False when end of instructions is reached
            pass
        return factory_map.crate_gps_coordinates

    def run_part_two(self):
        raw_map, raw_instructions = self.input_loader.load_input_array("\n\n")
        factory_map = parse_factory_map_wide_version(raw_map, parse_instructions(raw_instructions))

        while factory_map.process_next_instruction(wide_version=True):
            pass
        return factory_map.crate_gps_coordinates


def parse_instructions(raw_instructions: str) -> InstructionSet:
    direction_mapping = {
        "^": Direction.UP,
        "v": Direction.DOWN,
        "<": Direction.LEFT,
        ">": Direction.RIGHT,
    }
    return InstructionSet(
        [
            direction_mapping[char] for char in raw_instructions.strip().replace("\n", "")
        ]
    )


def parse_factory_map(raw_map: str, instructions: InstructionSet) -> FactoryMap:
    map_fields = []
    robot = None

    for row_id, raw_map_line in enumerate(raw_map.splitlines()):
        map_row = []
        for col_id, char in enumerate(raw_map_line):
            if char == "@":
                map_row.append(FactoryMapField(row=row_id, col=col_id, type=FieldType.EMPTY))
                robot = Robot(row=row_id, col=col_id)
            else:
                map_row.append(FactoryMapField(row=row_id, col=col_id, type=FieldType(char)))
        map_fields.append(map_row)

    return FactoryMap(fields=map_fields, instructions=instructions, robot=robot)


def parse_factory_map_wide_version(raw_map: str, instructions: InstructionSet) -> FactoryMap:
    map_fields = []
    robot = None

    for row_id, raw_map_line in enumerate(raw_map.splitlines()):
        map_row = []
        col_id = 0
        for char in raw_map_line:
            if char == "@":
                map_row.append(FactoryMapField(row=row_id, col=col_id, type=FieldType.EMPTY))
                map_row.append(FactoryMapField(row=row_id, col=col_id + 1, type=FieldType.EMPTY))
                robot = Robot(row=row_id, col=col_id)
            elif char == "O":
                map_row.append(FactoryMapField(row=row_id, col=col_id, type=FieldType.CRATE_LEFT))
                map_row.append(FactoryMapField(row=row_id, col=col_id + 1, type=FieldType.CRATE_RIGHT))
            else:  # for wall or empty
                map_row.append(FactoryMapField(row=row_id, col=col_id, type=FieldType(char)))
                map_row.append(FactoryMapField(row=row_id, col=col_id + 1, type=FieldType(char)))
            col_id += 2
        map_fields.append(map_row)

    return FactoryMap(fields=map_fields, instructions=instructions, robot=robot)
