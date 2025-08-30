from dataclasses import dataclass, field
from typing import Generator

from helpers import InputLoader
from lib.abstract_day import AbstractDay


RATIO_OF_LONE_ROBOTS_TO_SKIP_EVALUATION = 0.4
AVG_NEIGHBOUR_SCORE_CONSIDERED_IMAGE_THRESHOLD = 1.5
MAP_WIDTH = 101
MAP_HEIGHT = 103


@dataclass
class Robot:
    _initial_position_x: int
    _initial_position_y: int
    _velocity_x: int
    _velocity_y: int
    _current_position_x: int | None = None
    _current_position_y: int | None = None

    @property
    def current_col(self) -> int:
        if self._current_position_x is None:
            self._current_position_x = self._initial_position_x
        return self._current_position_x

    @current_col.setter
    def current_col(self, value):
        self._current_position_x = value

    @property
    def current_row(self) -> int:
        if self._current_position_y is None:
            self._current_position_y = self._initial_position_y
        return self._current_position_y

    @current_row.setter
    def current_row(self, value):
        self._current_position_y = value

    @property
    def current_position(self) -> tuple[int, int]:
        return self.current_col, self.current_row

    def move(self, board_width: int, board_height: int) -> None:
        new_col = self.current_col + self._velocity_x
        new_row = self.current_row + self._velocity_y

        while True:
            if new_col < 0:
                new_col += board_width
            elif new_col >= board_width:
                new_col -= board_width
            elif new_row < 0:
                new_row += board_height
            elif new_row >= board_height:
                new_row -= board_height
            else:
                break

        self.current_col = new_col
        self.current_row = new_row


@dataclass
class RobotMap:
    robots: list[Robot]
    width: int
    height: int
    _total_robots: int | None = None

    @property
    def total_robots(self) -> int:
        if self._total_robots is None:
            self._total_robots = len(self.robots)
        return self._total_robots

    def robot_positions(self) -> Generator[tuple[int, int], None, None]:
        return (robot.current_position for robot in self.robots)

    def move_robots(self) -> None:
        for robot in self.robots:
            robot.move(self.width, self.height)

    def calculate_robot_counts_in_quarants(self) -> tuple[int, int, int, int]:
        upper_left_quadrant = 0
        upper_right_quadrant = 0
        lower_left_quadrant = 0
        lower_right_quadrant = 0

        split_row = int(self.height / 2)
        split_col = int(self.width / 2)

        for robot_position_x, robot_position_y in self.robot_positions():
            if robot_position_x < split_col:
                if robot_position_y < split_row:
                    upper_left_quadrant += 1
                if robot_position_y > split_row:
                    lower_left_quadrant += 1
            if robot_position_x > split_col:
                if robot_position_y < split_row:
                    upper_right_quadrant += 1
                if robot_position_y > split_row:
                    lower_right_quadrant += 1

        return upper_left_quadrant, upper_right_quadrant, lower_left_quadrant, lower_right_quadrant

    def calculate_average_neighbour_score(self):
        robot_positions = set(self.robot_positions())
        neighbour_scores = []
        standalone_robots = 0

        for robot_position in robot_positions:
            neighbour_score = 0
            if (robot_position[0] + 1, robot_position[1]) in robot_positions:
                neighbour_score += 1
            if (robot_position[0] - 1, robot_position[1]) in robot_positions:
                neighbour_score += 1
            if (robot_position[0], robot_position[1] + 1) in robot_positions:
                neighbour_score += 1
            if (robot_position[0], robot_position[1] - 1) in robot_positions:
                neighbour_score += 1

            if neighbour_score == 0:
                standalone_robots += 1
                standalone_ratio = standalone_robots / self.total_robots
                if standalone_ratio > RATIO_OF_LONE_ROBOTS_TO_SKIP_EVALUATION:
                    return 0.0
            neighbour_scores.append(neighbour_score)

        return sum(neighbour_scores) / len(neighbour_scores)

    def print_map(self) -> None:
        robot_positions = list(self.robot_positions())
        for row in range(self.height):
            for col in range(self.width):
                print("#" if (col, row) in robot_positions else ".", end="")
            print()

    def print_map_with_count(self):
        robot_positions_count = {}
        for position in self.robot_positions():
            robot_positions_count.setdefault(position, 0)
            robot_positions_count[position] += 1

        for row in range(self.height):
            for col in range(self.width):
                print(robot_positions_count[(col, row)] if (col, row) in robot_positions_count else ".", end="")
            print()


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: InputLoader | None = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        raw_robot_lines = self.input_loader.load_input_array("\n")
        robot_map = load_robot_map(raw_robot_lines, width=MAP_WIDTH, height=MAP_HEIGHT)
        for _ in range(100):
            robot_map.move_robots()
        quadrants = robot_map.calculate_robot_counts_in_quarants()
        print(quadrants)
        return quadrants[0] * quadrants[1] * quadrants[2] * quadrants[3]

    def run_part_two(self):
        raw_robot_lines = self.input_loader.load_input_array("\n")
        robot_map = load_robot_map(raw_robot_lines, width=MAP_WIDTH, height=MAP_HEIGHT)

        for i in range(1, MAP_WIDTH*MAP_HEIGHT + 1):
            robot_map.move_robots()
            avg_neighbour_score = robot_map.calculate_average_neighbour_score()
            if avg_neighbour_score >= AVG_NEIGHBOUR_SCORE_CONSIDERED_IMAGE_THRESHOLD:
                return i

        return "Not found - increase limit of allowed robots not forming tree or neighbour threshold"


def load_robot_map(raw_robot_lines: str, width: int, height: int) -> RobotMap:
    robots = [assemble_robot(line) for line in raw_robot_lines]
    return RobotMap(robots=robots, width=width, height=height)


def assemble_robot(raw_robot_lines: str) -> Robot:
    raw_position, raw_velocity = raw_robot_lines.split(" ")
    raw_position_x, raw_position_y = raw_position.split("p=")[1].split(",")
    raw_velocity_x, raw_velocity_y = raw_velocity.split("v=")[1].split(",")
    return Robot(
        _initial_position_x=int(raw_position_x),
        _initial_position_y=int(raw_position_y),
        _velocity_x=int(raw_velocity_x),
        _velocity_y=int(raw_velocity_y),
    )
