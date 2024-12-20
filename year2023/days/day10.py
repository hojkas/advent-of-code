from enum import Enum
from typing import Optional

from lib.abstract_day import AbstractDay
from helpers import InputLoader, Direction
from lib.exceptions import RunException


class NeighbourOutOfBoundsException(RunException):
    """
    Exception raised when a pipe seeks neighbour out of bounds.
    """


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


class PipeLocationType(Enum):
    LOOP = 0
    LEFT_HANDED_AREA = 1
    RIGHT_HANDED_AREA = 2
    UNDECIDED = 3

    @property
    def opposite(self) -> 'PipeLocationType':
        if self == PipeLocationType.RIGHT_HANDED_AREA:
            return PipeLocationType.LEFT_HANDED_AREA
        if self == PipeLocationType.LEFT_HANDED_AREA:
            return PipeLocationType.RIGHT_HANDED_AREA
        raise RunException(f"Cannot deterine opposite of location type {self.name}")


class Pipe:
    def __init__(self, representation: str, row: int, col: int):
        self.row = row
        self.col = col
        self.type = PIPE_TYPE_TRANSLATION[representation]
        self.neighbours: dict[Direction, Optional['Pipe']] = {direction: None for direction in Direction}
        self.is_start = True if representation == "S" else False
        self.is_empty = self.type == PipeType.NONE
        self.location = PipeLocationType.UNDECIDED

    def __repr__(self):
        return f"Pipe({self.type}, {self.row}, {self.col}, {self.location})"

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


class OrientedPipe:
    def __init__(self, pipe: Pipe, entry_direction: Direction, exit_direction: Direction) -> None:
        self.pipe = pipe
        self.entry_direction = entry_direction
        self.exit_direction = exit_direction

    def __repr__(self):
        return f"{self.pipe} <{self.entry_direction} {self.exit_direction}>"

    def get_left_hand_directions(self):
        directions = []
        curr_direction = self.entry_direction.next_clockwise_cardinal
        while curr_direction != self.exit_direction:
            directions.append(curr_direction)
            curr_direction = curr_direction.next_clockwise_cardinal
        return directions

    def get_right_hand_directions(self):
        directions = []
        curr_direction = self.exit_direction.next_clockwise_cardinal
        while curr_direction != self.entry_direction:
            directions.append(curr_direction)
            curr_direction = curr_direction.next_clockwise_cardinal
        return directions


class PipeMap:
    def __init__(self, input_lines: list[str]) -> None:
        self.pipes: list[list[Pipe]] = []
        self.loop: list[OrientedPipe] = []

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

    def determine_inner_location_type(self) -> PipeLocationType:
        # check the first line
        for pipe in self.pipes[0]:
            if pipe.location in [PipeLocationType.LEFT_HANDED_AREA, PipeLocationType.RIGHT_HANDED_AREA]:
                return pipe.location.opposite
        # and the last
        for pipe in self.pipes[-1]:
            if pipe.location in [PipeLocationType.LEFT_HANDED_AREA, PipeLocationType.RIGHT_HANDED_AREA]:
                return pipe.location.opposite
        # and first and last columns
        for pipe_line in self.pipes:
            if pipe_line[0].location in [PipeLocationType.LEFT_HANDED_AREA, PipeLocationType.RIGHT_HANDED_AREA]:
                return pipe_line[0].location.opposite
            if pipe_line[-1].location in [PipeLocationType.LEFT_HANDED_AREA, PipeLocationType.RIGHT_HANDED_AREA]:
                return pipe_line[-1].location.opposite
        # finally, if none of the edge fields had location (hence the full edge is a loop), pick the only area present
        for pipe_line in self.pipes[1:-1]:
            for pipe in pipe_line[1:-1]:
                if pipe.location in [PipeLocationType.LEFT_HANDED_AREA, PipeLocationType.RIGHT_HANDED_AREA]:
                    return pipe.location

        raise RunException("Cannot determine inner location type")

    def count_pipes_with_location_type(self, location_type: PipeLocationType) -> int:
        count = 0
        for pipe_line in self.pipes:
            for pipe in pipe_line:
                if pipe.location == location_type:
                    count += 1
        return count

    def print(self):
        for pipe_line in self.pipes:
            for pipe in pipe_line:
                char = {
                    PipeLocationType.LOOP: "#",
                    PipeLocationType.UNDECIDED: "?",
                    PipeLocationType.LEFT_HANDED_AREA: "o",
                    PipeLocationType.RIGHT_HANDED_AREA: "i",
                }[pipe.location]
                print(char, end="")
            print()


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
    _mark_loop_pipes(pipe_map)
    _flood_fill_map(pipe_map)
    inner_location_type = pipe_map.determine_inner_location_type()
    return pipe_map.count_pipes_with_location_type(inner_location_type)


def _mark_loop_pipes(pipe_map: PipeMap) -> None:
    starting_pipe = pipe_map.starting_pipe
    previous_exit_direction, _ = starting_pipe.get_directions()
    previous_pipe = starting_pipe
    starting_pipe.location = PipeLocationType.LOOP

    while True:
        current_entry_direction = previous_exit_direction.opposite
        current_pipe = previous_pipe.get_neighbour_in_direction(previous_exit_direction)
        current_exit_direction = current_pipe.get_exit_direction(current_entry_direction)

        if current_pipe == starting_pipe:
            break

        pipe_map.loop.append(OrientedPipe(current_pipe, current_entry_direction, current_exit_direction))
        current_pipe.location = PipeLocationType.LOOP

        previous_pipe = current_pipe
        previous_exit_direction = current_exit_direction


def _flood_fill_map(pipe_map: PipeMap) -> None:
    for oriented_pipe in pipe_map.loop:
        _flood_fill_from_pipe(oriented_pipe)


def _flood_fill_from_pipe(oriented_loop_pipe: OrientedPipe) -> None:
    left_hand_directions = oriented_loop_pipe.get_left_hand_directions()
    right_hand_directions = oriented_loop_pipe.get_right_hand_directions()

    for left_direction in left_hand_directions:
        try:
            neighbour_in_left_direction = oriented_loop_pipe.pipe.get_neighbour_in_direction(left_direction)
            _mark_neighbour_and_flood(neighbour_in_left_direction, PipeLocationType.LEFT_HANDED_AREA)
        except NeighbourOutOfBoundsException:
            pass

    for right_direction in right_hand_directions:
        try:
            neighbour_in_right_direction = oriented_loop_pipe.pipe.get_neighbour_in_direction(right_direction)
            _mark_neighbour_and_flood(neighbour_in_right_direction, PipeLocationType.RIGHT_HANDED_AREA)
        except NeighbourOutOfBoundsException:
            pass


def _mark_neighbour_and_flood_old(pipe: Pipe, location_type: PipeLocationType) -> None:
    if pipe.location != PipeLocationType.UNDECIDED:
        return  # already has a type, nowhere to flood

    pipe.location = location_type
    for neighbour in pipe.neighbours.values():
        if neighbour is not None:
            _mark_neighbour_and_flood(neighbour, location_type)


def _mark_neighbour_and_flood(first_pipe: Pipe, location_type: PipeLocationType) -> None:
    if first_pipe.location != PipeLocationType.UNDECIDED:
        return

    pipes_to_flood = [first_pipe]

    while pipes_to_flood:
        pipe = pipes_to_flood.pop()
        pipe.location = location_type
        for neighbour in pipe.neighbours.values():
            if neighbour is not None and neighbour.location == PipeLocationType.UNDECIDED:
                pipes_to_flood.append(neighbour)
