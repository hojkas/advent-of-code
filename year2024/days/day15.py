from dataclasses import dataclass
from enum import StrEnum

from helpers import InputLoader
from lib.abstract_day import AbstractDay
from lib.models import Direction, GenericMapField, GenericMapRepresentation


class NoMoreInstructions(Exception):
    """
    No more instructions available.
    """


class FieldType(StrEnum):
    WALL = "#"
    EMPTY = "."
    CRATE = "O"


@dataclass
class Robot(GenericMapField):
    pass


@dataclass
class InstructionSet:
    instructions: list[Direction]
    current_index: int = 0

    def next_instruction(self, loop: bool = False) -> Direction | None:
        if self.current_index >= len(self.instructions):
            if loop:
                self.current_index = 0
            else:
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


@dataclass
class FactoryMap(GenericMapRepresentation):
    fields: list[list[FactoryMapField]]
    instructions: InstructionSet
    robot: Robot

    @property
    def crate_gps_coordinates(self) -> int:
        gps_sum = 0
        for row in self.fields:
            for field in row:
                if field.type == FieldType.CRATE:
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

    def process_next_instruction(self, loop: bool = False):
        instruction = self.instructions.next_instruction(loop)
        if instruction is None:
            raise NoMoreInstructions()

        if self.robot_can_move(instruction):
            self.move_robot(instruction)

    def robot_can_move(self, direction: Direction) -> bool:
        current_field = self.robot
        while True:
            next_field = self.get_next_field_in_direction(current_field, direction)
            if next_field.type == FieldType.WALL:
                return False
            if next_field.type == FieldType.EMPTY:
                return True
            current_field = next_field


    def move_robot(self, instruction: Direction):
        next_field_to_resolve = self.get_next_field_in_direction(self.robot, instruction)
        self.robot.row += instruction.value[0]
        self.robot.col += instruction.value[1]

        if next_field_to_resolve.type == FieldType.EMPTY:
            return
        else:
            next_field_to_resolve.type = FieldType.EMPTY  # set empty as robot pushed it out

        while True:
            next_field_to_resolve = self.get_next_field_in_direction(next_field_to_resolve, instruction)
            if next_field_to_resolve.type == FieldType.EMPTY:
                next_field_to_resolve.type = FieldType.CRATE
                return



class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: InputLoader | None = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        raw_map, raw_instructions = self.input_loader.load_input_array("\n\n")
        factory_map = parse_factory_map(raw_map, parse_instructions(raw_instructions))

        try:
            while True:
                factory_map.process_next_instruction(loop=False)
        except NoMoreInstructions:
            pass
        return factory_map.crate_gps_coordinates

    def run_part_two(self):
        return "---"


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
