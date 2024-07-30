from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from lib.abstract_day import AbstractDay
from helpers import InputLoader
from lib.exceptions import RunException


class NeighbourOutOfBoundsException(RunException):
    """
    Exception raised when a pipe seeks neighbour out of bounds.
    """


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

    @property
    def opposite(self):
        return {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }[self]


class PipeType(Enum):
    UP_RIGHT = "L"
    UP_LEFT = "J"
    DOWN_RIGHT = "F"
    DOWN_LEFT = "7"
    LEFT_RIGHT = "-"
    UP_DOWN = "|"
    UNDECIDED = "?"
    NONE = "-"

    def get_directions(self) -> tuple[Direction, Direction]:
        directions = []
        for direction in Direction:
            if direction.name in self.name:
                directions.append(direction)
        if len(directions) != 2:
            raise RunException("Pipe type must contain 2 directions")
        return directions[0], directions[1]


PIPE_TYPE_TRANSLATION = {
    "L": PipeType.UP_RIGHT,
    "J": PipeType.UP_LEFT,
    "F": PipeType.DOWN_RIGHT,
    "7": PipeType.DOWN_LEFT,
    "-": PipeType.LEFT_RIGHT,
    "|": PipeType.UP_DOWN,
    "S": PipeType.UNDECIDED,
    ".": PipeType.NONE,
}


class PipeLocationtype(Enum):
    LOOP = 0
    INSIDE = 1
    OUTSIDE = 2
    UNDECIDED = 3


class Pipe:
    def __init__(self, representation: str, row: int, col: int):
        self.row = row
        self.col = col
        self.type = PIPE_TYPE_TRANSLATION[representation]
        self.neighbours: dict[Direction, Optional['Pipe']] = {direction: None for direction in Direction}
        self.is_start = True if representation == "S" else False
        self.is_empty = self.type == PipeType.NONE
        self.location = PipeLocationtype.UNDECIDED

    def __repr__(self):
        return f"Pipe({self.type}, {self.row}, {self.col})"

    def goes_in_direction(self, direction: Direction) -> bool:
        return direction in self.get_directions()

    def get_directions(self) -> tuple[Direction, Direction]:
        return self.type.get_directions()

    def get_exit_direction(self, entry_direction: Direction) -> Direction:
        possible_directions = []
        for possible_direction in self.get_directions():
            if possible_direction != entry_direction:
                possible_directions.append(possible_direction)
        if len(possible_directions) == 0:
            raise RunException("Cannot find exit direction")
        if len(possible_directions) > 1:
            raise RunException("Found more than one exit direction, logic is flawed.")
        return possible_directions[0]

    def get_neighbour_in_direction(self, direction: Direction) -> 'Pipe':
        neighbour = self.neighbours[direction]
        if neighbour is None:
            raise NeighbourOutOfBoundsException(
                f"Cannot find neighbour in direction {direction.name} for pipe on {self.row}, {self.col}"
            )
        return neighbour


class PipeMap:
    def __init__(self, input_lines: list[str]) -> None:
        self.pipes = []
        starting_node = None
        for row, line in enumerate(input_lines):
            pipe_row = []
            for col, char in enumerate(line):
                pipe = Pipe(char, row, col)
                pipe_row.append(pipe)
                if pipe.is_start:
                    starting_node = pipe
            self.pipes.append(pipe_row)

        self._load_neighbours()
        self._resolve_starting_pipe_type(starting_node)
        self.starting_pipe = starting_node

    def _load_neighbours(self) -> None:
        for row, pipe_line in enumerate(self.pipes):
            for col, pipe in enumerate(pipe_line):
                for direction in Direction:
                    pipe.neighbours[direction] = self._get_pipe_on_coordinates(
                        row + direction.value[0], col + direction.value[1]
                    )

    def _get_pipe_on_coordinates(self, row, col) -> Optional[Pipe]:
        if row < 0 or col < 0:
            return None
        try:
            return self.pipes[row][col]
        except IndexError:
            return None

    @staticmethod
    def _resolve_starting_pipe_type(starting_node):
        if starting_node is None:
            raise RunException("Cannot find starting node")
        connected_directions = []
        for direction in Direction:
            try:
                neighbour = starting_node.get_neighbour_in_direction(direction)
                if neighbour.goes_in_direction(direction.opposite):
                    connected_directions.append(direction)
            except NeighbourOutOfBoundsException:
                continue
        if len(connected_directions) != 2:
            raise RunException(
                f"Failed to resolve start: had unexpected number of connections. {connected_directions}"
            )
        for pipe_type in PipeType:
            if connected_directions[0].name in pipe_type.name and connected_directions[1].name in pipe_type.name:
                starting_node.type = pipe_type
                break
        if starting_node.type == PipeType.UNDECIDED:
            raise RunException("Cannot decide for PipeType UNDECIDED")


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_lines = self.input_loader.load_input_array(item_separator="\n")
        pipe_map = PipeMap(input_lines)
        result = run_part_one(pipe_map)
        return result

    def run_part_two(self):
        input_lines = self.input_loader.load_input_array(item_separator="\n")
        pipe_map = PipeMap(input_lines)
        result = run_part_two(pipe_map)
        return result


def run_part_one(pipe_map: PipeMap) -> int:
    starting_pipe = pipe_map.starting_pipe
    steps = 0
    first_direction, second_direction = starting_pipe.get_directions()
    first_new_pipe = starting_pipe
    second_new_pipe = starting_pipe

    while True:
        steps += 1
        first_new_pipe = first_new_pipe.get_neighbour_in_direction(first_direction)
        second_new_pipe = second_new_pipe.get_neighbour_in_direction(second_direction)

        if first_new_pipe == starting_pipe or second_new_pipe == starting_pipe:
            print(f"Failed after {steps} steps")
            return -1
        if first_new_pipe == second_new_pipe:
            return steps

        first_direction = first_new_pipe.get_exit_direction(first_direction.opposite)
        second_direction = second_new_pipe.get_exit_direction(second_direction.opposite)


def run_part_two(pipe_map: PipeMap) -> int:
    pass
