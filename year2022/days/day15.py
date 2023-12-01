from typing import Union
from lib.abstract_day import AbstractDay
from helpers import regex_extract_multiple, Range, InputLoader
from lib.exceptions import RunException

"""
DIAGONAL SPACE explanation
==========================

NOTE: Diagonal space is used solely in part 2.

The whole idea of diagonal space and the calculations between two spaces
count with x>=0 and y>=0 restriction in cartese space, with x=0 and y=0 being the start of measured space

main diagonals (sd): \\\\\\\
numbered <-(square_size-1), +(square_size-1)>, longest diagonal 0 goes through [0,0] [1,1] etc.
side diagonals (md): ///////
numbered <0, 2*(square_size-1)>, the longest one is number (square_size - 1)

NOTE: square_size = max_x/max_y + 1, I'm always counting with x/y starting on 0

when in diagonal space, the reach of every scanner is square (instead of diamond)
with side long (manhattan_to_beacon)*2 + 1, allowing for quicker calculations

Conversions:
md = x - y
sd = x + y
x = md + y
y = (sd - md)/2

Check if diagonal are withing cartensian space:
sd + md >= 0
sd + md <= 2*(square_size-1)
sd - md >= 0
sd - md <= 2*(square_size-1)

Example:
(S - scanner, B - beacon, . - not reaching, # - reaching, _ - out of bounds, " " - invalid square in diagonal)
Cartesian space:
  0 1 2 3
0 . # . .
1 # # B .
2 # S # #
3 # # # .

Beacon manhattan distance: 2
Scanner position in diagonal space: MD -1, SD 3
Beacon position in diagonal space: MD 1, SD 3

Diagonal space: (the same case, minx/y 0, maxx/y 3)
SD\MD -3-2-1 0 1 2 3
0        _   .   _  
1      _   #   #   _
2        #   #   .  
3      #   S   B   .
4        #   #   .  
5      _   #   #   _
6        _   .   _  

In diagonal space, S scans the whole square on md <-3;1>, sd <1,5>
"""


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.md = x - y  # main diagonale
        self.sd = x + y  # side diagonale

    @staticmethod
    def can_be_constructed_from_diagonal(md, sd):
        return (sd - md) % 2 == 0

    @staticmethod
    def from_diagonal(md, sd):
        if not Coordinate.can_be_constructed_from_diagonal(md, sd):
            raise RunException(f"Invalid coordinates in cartesan space. md {md}, sd {sd}")
        y = 0.5 * (sd - md)
        x = md + y
        return Coordinate(x, y)

    def manhattan(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)


def normalize(r: Range, min_val, max_val) -> Range:
    new_start = min_val if r.start < min_val else r.start
    new_end = max_val if max_val < r.end else r.end
    return Range(new_start, new_end)


class CartesianAndDiagonalSpaceBinding:
    def __init__(self, max_value):
        self.cartesian_max_value = max_value

    def cartesian_in_bounds(self, x, y):
        return (0 <= x <= self.cartesian_max_value) and (0 <= y <= self.cartesian_max_value)

    def diagonal_in_bounds(self, md, sd):
        return (0 <= sd + md <= 2 * self.cartesian_max_value) and (0 <= sd - md <= 2 * self.cartesian_max_value)

    def md_possible_range_for_fixed_sd(self, sd):
        boundary = sd
        alt_boundary = 2 * self.cartesian_max_value - sd
        if alt_boundary < boundary:
            return Range(-alt_boundary, alt_boundary)
        return Range(-boundary, boundary)

    def max_md_possible_range_for_sd_range(self, sd_range: Range):
        peak_sd = self.cartesian_max_value
        if peak_sd in sd_range:
            return self.md_possible_range_for_fixed_sd(peak_sd)
        start_md_range = self.md_possible_range_for_fixed_sd(sd_range.start)
        end_md_range = self.md_possible_range_for_fixed_sd(sd_range.end)
        return start_md_range if len(start_md_range) > len(end_md_range) else end_md_range

    def sd_possible_range(self):
        return Range(0, 2*self.cartesian_max_value)


class Sensor:
    def __init__(self, input_line):
        extracted = regex_extract_multiple(r"Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)",
                                           input_line, 4)

        self.position = Coordinate(x=int(extracted[0]), y=int(extracted[1]))
        self.beacon_position = Coordinate(x=int(extracted[2]), y=int(extracted[3]))
        self.beacon_distance = self.position.manhattan(self.beacon_position)
        self.diagonal_min_md = self.position.md - self.beacon_distance
        self.diagonal_max_md = self.position.md + self.beacon_distance
        self.diagonal_min_sd = self.position.sd - self.beacon_distance
        self.diagonal_max_sd = self.position.sd + self.beacon_distance

        self.md_range = Range(self.diagonal_min_md, self.diagonal_max_md)

    def point_within_sensor(self, md, sd):
        return ((self.diagonal_min_md <= md <= self.diagonal_max_md) and
                (self.diagonal_min_sd <= sd <= self.diagonal_max_sd))

    def affected_range_on_y(self, y) -> Union[None, Range]:
        x_wiggle_room = self.beacon_distance - abs(self.position.y - y)
        if x_wiggle_room < 0:
            return None
        x_wiggle_room = abs(x_wiggle_room)
        return Range(self.position.x - x_wiggle_room, self.position.x + x_wiggle_room)

    def affected_range_on_sd(self, sd) -> Union[None, Range]:
        if self.diagonal_min_sd <= sd <= self.diagonal_max_sd:
            return Range(self.diagonal_min_md, self.diagonal_max_md)
        return None


def construct_sensors(input_array):
    sensors = []
    for line in input_array:
        sensors.append(Sensor(line))
    return sensors


def extract_scanned_ranges(distance_goal, sensors) -> list[Range]:
    raw_ranges = [s.affected_range_on_y(distance_goal) for s in sensors]
    ranges = [r for r in raw_ranges if r is not None]
    ranges.sort(key=lambda r: r.start)
    return ranges


def process_range(r, last_checked_point) -> tuple[int, int]:
    # range adds itself whole to the scanned points
    if not last_checked_point or last_checked_point < r.start:
        return r.end, (r.end - r.start + 1)

    # range doesn't add anything to the scanned points
    if last_checked_point > r.end:
        return last_checked_point, 0

    # range adds some to the scanned points
    return r.end, r.end - last_checked_point


def beacon_count_on_y(sensors, y):
    c = 0
    beacons = []
    for sensor in sensors:
        if sensor.beacon_position.y == y and len([b for b in beacons if b.x == sensor.beacon_position.x]) == 0:
            c += 1
            beacons.append(sensor.beacon_position)
    return c


def part_one(sensors, distance_goal):
    ranges = extract_scanned_ranges(distance_goal, sensors)
    checked_points = 0
    last_checked_point = None
    for r in ranges:
        last_checked_point, new_checked_points = process_range(r, last_checked_point)
        checked_points += new_checked_points
    checked_points -= beacon_count_on_y(sensors, distance_goal)
    return checked_points


def find_not_covered_md(md_range: Range, scanner_md_ranges: list[Range]):
    not_covered = []
    scanner_md_ranges.sort(key=lambda x: x.start)
    first_unscanned_md = md_range.start
    for r in scanner_md_ranges:
        if r.end < first_unscanned_md:
            continue
        elif r.start <= first_unscanned_md:
            first_unscanned_md = r.end + 1
        else:
            not_covered.append(Range(first_unscanned_md, r.start - 1))
            first_unscanned_md = r.end + 1

    return not_covered


def part_two(sensors, max_xy_value):
    space = CartesianAndDiagonalSpaceBinding(max_xy_value)
    sd_range = space.sd_possible_range()
    sd = sd_range.start
    unscanned = []
    while sd <= sd_range.end:
        md_range = space.md_possible_range_for_fixed_sd(sd)
        sensor_md_ranges = [s.md_range for s in sensors if (s.diagonal_min_sd <= sd <= s.diagonal_max_sd)]
        not_covered = find_not_covered_md(md_range, sensor_md_ranges)
        if not_covered:
            for r in not_covered:
                for md in r:
                    if Coordinate.can_be_constructed_from_diagonal(md, sd):
                        unscanned.append(Coordinate.from_diagonal(md, sd))
        sd += 1

    if len(unscanned) == 1:
        return int(unscanned[0].x * 4000000 + unscanned[0].y)
    else:
        raise RunException(unscanned)


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        sensors = construct_sensors(self.input_loader.load_input_array("\n"))
        result = part_one(sensors, 2000000)
        return result

    def run_part_two(self):
        sensors = construct_sensors(self.input_loader.load_input_array("\n"))
        result = part_two(sensors, 4000000)
        return result
