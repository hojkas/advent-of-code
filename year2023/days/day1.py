from typing import Union

import regex as re

from helpers import InputLoader
from lib.abstract_day import AbstractDay
from lib.exceptions import RunException


WORDS_TO_DIGITS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}


ALL_DIGITS_REGEX = r"(one|two|three|four|five|six|seven|eight|nine|\d)"


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_array = self.input_loader.load_input_array(item_separator="\n")
        result = part_one(input_array)
        return result

    def run_part_two(self):
        input_array = self.input_loader.load_input_array(item_separator="\n")
        result = part_two(input_array)
        return result


def part_one(input_array: list[str]) -> int:
    s = 0
    for line in input_array:
        s += calculate_line_value(line)
    return s


def part_two(input_array: list[str]) -> int:
    # TODO works on test input, but is still wrong (54100 is too high, 53432 is too low)
    s = 0
    for line in input_array:
        s += calculate_line_value_v2(line)
    return s


def calculate_line_value_v2(line: str) -> int:
    # this part is done one by one via regex and not all at once to avoid wrong replacement
    # e.g. twone needs to be replaced as 2ne, not tw1 (which would be result of batch replacement)
    # regex already deals with the overlapping just like we need it
    matches = re.findall(ALL_DIGITS_REGEX, line, overlapped=True)
    first_num = matches[0] if matches[0].isdigit() else WORDS_TO_DIGITS[matches[0]]
    last_num = matches[-1] if matches[-1].isdigit() else WORDS_TO_DIGITS[matches[-1]]
    return int(first_num) * 10 + int(last_num)


def calculate_line_value(line: str) -> int:
    first_num = find_first_digit(line)
    last_num = find_first_digit(line[::-1])
    return first_num * 10 + last_num


def find_first_digit(line: str) -> int:
    for char in line:
        if char.isdigit():
            return int(char)
    raise RunException(f"No digit found in line {line}")

