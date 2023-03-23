from enum import Enum
from typing import Union
from abstract_day import AbstractDay
from helpers.input_loader import InputLoader
from exceptions import RunException


class OutOfBoundsError(RunException):
    pass


class AlreadyVisitedError(RunException):
    pass


def letter_to_height(letter):
    if letter == "S":
        return 0
    if letter == "E":
        return 25
    if ord("a") <= ord(letter) <= ord("z"):
        return ord(letter) - ord("a")
    raise RunException(f"Given letter {letter} is not a-z nor S or E, the only allowed letters.")


class Direction(Enum):
    UP = (-1, 0)
    LEFT = (0, -1)
    DOWN = (1, 0)
    RIGHT = (0, 1)


class Field:
    def __init__(self, row, col, letter_height, field_id):
        self.height = letter_to_height(letter_height)
        self.start = True if letter_height == "S" else False
        self.end = True if letter_height == "E" else False
        self.row = row
        self.col = col
        self.id = field_id


class Map:
    def __init__(self, input_array):
        self.row_count = len(input_array)
        self.col_count = len(input_array[0])
        self.fields = []
        self.start = None
        self.end = None
        self._load_fields(input_array)
        self._find_start_and_end()

    def _load_fields(self, input_array):
        field_id = 0
        for row_id, row in enumerate(input_array):
            row_items = []
            for col_id, item in enumerate(row):
                row_items.append(Field(row_id, col_id, item, field_id))
                field_id += 1
            self.fields.append(row_items)

    def _find_start_and_end(self):
        for row in self.fields:
            for item in row:
                if item.start:
                    self.start = item
                if item.end:
                    self.end = item
                if self.start and self.end:
                    return

    def _coordinates_within_bounds(self, row, col):
        return 0 <= row < self.row_count and 0 <= col < self.col_count

    def grab_relative_field(self, field, direction):
        new_row = field.row + direction.value[0]
        new_col = field.col + direction.value[1]
        if not self._coordinates_within_bounds(new_row, new_col):
            raise OutOfBoundsError()
        new_field = self.fields[new_row][new_col]
        return new_field


class Route:
    def __init__(self, og_route=None):
        if og_route:
            self.visited = og_route.visited.copy()
        else:
            self.visited = []
        self.last_field = None

    def visited_field(self, field: Field):
        return field.id in self.visited

    def route_length(self):
        return len(self.visited) - 1

    def add_visited(self, field: Field):
        if self.visited_field(field):
            raise AlreadyVisitedError(f"This route already visited {field.id}")
        self.visited.append(field.id)
        self.last_field = field


class RouteFinder:
    def __init__(self, height_map):
        self.map = height_map
        self.best_waypoints = {}
        self.routes_to_check = []
        self.best_route_cost = None

    def _move_possible(self, field: Field, direction: Direction):
        try:
            return self.map.grab_relative_field(field, direction).height <= field.height + 1
        except OutOfBoundsError:
            return False

    def _reverse_move_possible(self, field: Field, direction: Direction):
        try:
            return self.map.grab_relative_field(field, direction).height + 1 >= field.height
        except OutOfBoundsError:
            return False

    def _note_cost_and_asses_worthiness(self, new_field, new_cost):
        if new_field.id not in self.best_waypoints.keys():
            self.best_waypoints[new_field.id] = new_cost
            return True
        if new_cost < self.best_waypoints[new_field.id]:
            self.best_waypoints[new_field.id] = new_cost
            return True
        return False

    def asign_best_result(self, new_route_length):
        if not self.best_route_cost:
            self.best_route_cost = new_route_length

        if new_route_length < self.best_route_cost:
            self.best_route_cost = new_route_length

    def _check_route(self, route):
        for direction in Direction:
            if not self._move_possible(route.last_field, direction):
                continue

            new_field = self.map.grab_relative_field(route.last_field, direction)
            if route.visited_field(new_field):
                continue

            new_route = Route(route)
            new_route.add_visited(new_field)

            if new_field.end:
                new_route_length = new_route.route_length()
                self.asign_best_result(new_route_length)
                continue

            if not self._note_cost_and_asses_worthiness(new_field, new_route.route_length()):
                continue

            self.routes_to_check.append(new_route)

    def find_route(self):
        current_field = self.map.start
        default_route = Route()
        default_route.add_visited(current_field)
        self.routes_to_check.append(default_route)

        while True:
            if len(self.routes_to_check) == 0:
                break
            next_route = self.routes_to_check.pop(0)
            self._check_route(next_route)

        return self.best_route_cost


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_array = self.input_loader.load_input_array("\n")
        field_map = Map(input_array)
        result = RouteFinder(field_map).find_route()
        return result

    def run_part_two(self):
        return "---"
