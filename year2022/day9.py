import os
from typing import Union
from abstract_day import AbstractDay
from exceptions import RunException
from helpers import CC
from input_loader import InputLoader


def print_result(part, result):
    filename = os.path.basename(__file__).split('.')[0]
    print('[', filename, '] ', CC.GREEN, 'Result of part ', part, CC.NC, ': ', result, sep='')


class Direction:
    @staticmethod
    def translate_to_coords(letter):
        letter = letter.lower()
        if letter == "d":
            return Coordinate(0, -1)
        if letter == "u":
            return Coordinate(0, 1)
        if letter == "r":
            return Coordinate(1, 0)
        if letter == "l":
            return Coordinate(-1, 0)
        raise RunException("Unknown direction")


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __hash__(self):
        return hash(str(self.x) + str(self.y))

    def __str__(self):
        return "[" + str(self.x) + ";" + str(self.y) + "]"

    def __repr__(self):
        return "[" + str(self.x) + ";" + str(self.y) + "]"

    def copy(self):
        return Coordinate(self.x, self.y)

    def same_x(self, other):
        return self.x == other.x

    def same_y(self, other):
        return self.y == other.y

    def same_x_or_y(self, other):
        return self.y == other.y or self.x == other.x

    def touching_or_diagonal_or_same(self, other):
        return abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1


class Rope:
    def __init__(self):
        self.head = Coordinate(0, 0)
        self.tail = Coordinate(0, 0)
        self.visited = {self.tail.copy()}

    def long_move(self, instruction: str):
        direction_s, count_s = instruction.split(" ")
        direction = Direction.translate_to_coords(direction_s)
        count = int(count_s)
        for _ in range(count):
            self._one_move(direction)

    def _one_move(self, direction: Coordinate):
        self._move_head(direction)
        self._adjust_tail(direction)

    def _move_head(self, direction: Coordinate):
        self.head = self.head + direction

    def _adjust_tail(self, head_direction: Coordinate):
        if self.tail.touching_or_diagonal_or_same(self.head):
            return

        if self.tail.same_x_or_y(self.head):
            self.tail += head_direction
        else:  # not in the same row or col
            self.tail = self.head - head_direction

        self._mark_tail_position()

    def _mark_tail_position(self):
        self.visited.add(self.tail.copy())

    def tail_visited_count(self):
        return len(self.visited)


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None
        self.debug_mode = False

    def dbg(self, *args, **kwargs):
        if self.debug_mode:
            print(*args, **kwargs)

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def use_debug(self, use_debug=False):
        self.debug_mode = use_debug

    def run_part_one(self):
        input_array = self.input_loader.load_input_array("\n")
        rope = Rope()
        for line in input_array:
            rope.long_move(line)
        result = rope.tail_visited_count()
        print_result(1, result)

    def run_part_two(self):
        print_result(2, '---')
