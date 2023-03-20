import os
from typing import Union
from abstract_day import AbstractDay
from exceptions import RunException
from old_helpers import CC
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

    def cut_values_to_one(self):
        if self.x > 1:
            self.x = 1
        elif self.x < -1:
            self.x = -1

        if self.y > 1:
            self.y = 1
        elif self.y < -1:
            self.y = -1


class Rope:
    def __init__(self, lenght):
        self.rope_chain = [Coordinate(0, 0) for _ in range(lenght)]
        self.lenght = len(self.rope_chain)
        self.visited = {Coordinate(0, 0)}

    def long_move(self, instruction: str):
        direction_s, count_s = instruction.split(" ")
        direction = Direction.translate_to_coords(direction_s)
        count = int(count_s)
        for _ in range(count):
            self._one_move(direction)

    def _one_move(self, direction: Coordinate):
        self._move_head(direction)  # first one moves without restrictions
        for i in range(self.lenght - 1):  # last one doesn't have one behind to affect
            self._adjust_following(i, i+1)
        self._mark_tail_position()

    def _move_head(self, direction: Coordinate):
        self.rope_chain[0] = self.rope_chain[0] + direction

    def _adjust_following(self, lead_i, follow_i):
        if self.rope_chain[follow_i].touching_or_diagonal_or_same(self.rope_chain[lead_i]):
            return

        lead_follow_diff = (self.rope_chain[lead_i] - self.rope_chain[follow_i])
        lead_follow_diff.cut_values_to_one()
        self.rope_chain[follow_i] = self.rope_chain[follow_i] + lead_follow_diff

    def _mark_tail_position(self):
        self.visited.add(self.rope_chain[-1].copy())

    def tail_visited_count(self):
        return len(self.visited)

    def print_state(self):
        minx = min(self.rope_chain, key=lambda c: c.x).x
        if minx > -10:
            minx = -10
        miny = min(self.rope_chain, key=lambda c: c.y).y
        if miny > -10:
            miny = -10
        maxx = max(self.rope_chain, key=lambda c: c.x).x
        if maxx < 10:
            maxx = 10
        maxy = max(self.rope_chain, key=lambda c: c.y).y
        if maxy < 10:
            maxy = 10

        draw_board = [["." for _ in range(maxx - minx + 1)] for _ in range(maxy - miny + 1)]
        for i, coord in enumerate(self.rope_chain):
            draw_board[coord.y - miny][coord.x - minx] = str(i + 1)
        for row in draw_board:
            for col in row:
                print(col, end="")
            print()
        print("---")


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
        rope = Rope(2)
        for line in input_array:
            rope.long_move(line)
        result = rope.tail_visited_count()
        print_result(1, result)

    def run_part_two(self):
        input_array = self.input_loader.load_input_array("\n")
        rope = Rope(10)
        for line in input_array:
            rope.long_move(line)
        result = rope.tail_visited_count()
        print_result(2, result)
