from dataclasses import dataclass
from typing import Optional
import re

from lib.abstract_day import AbstractDay
from helpers import InputLoader


BASIC_MULTIPLICATION_REGEX = r"mul\(\d+,\d+\)"
DO_DONT_MUL_REGEX = r"(mul\(\d+,\d+\)|do(n't)?\(\))"


class MultiplicationItem:
    def __init__(self, string: str):
        first_number_string, second_number_string = string.replace("mul(", "").replace(")", "").split(",")
        self.first_number = int(first_number_string)
        self.second_number = int(second_number_string)


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        multiplications = load_multiplications(self.input_loader.load_input())
        return sum((mi.first_number * mi.second_number for mi in multiplications))

    def run_part_two(self):
        multiplications = load_only_valid_multiplications(self.input_loader.load_input())
        return sum((mi.first_number * mi.second_number for mi in multiplications))


def load_multiplications(input_string: str) -> list[MultiplicationItem]:
    multiplication_items = []
    for multiplication_string in re.findall(BASIC_MULTIPLICATION_REGEX, input_string):
        multiplication_items.append(MultiplicationItem(multiplication_string))
    return multiplication_items


def load_only_valid_multiplications(input_string: str) -> list[MultiplicationItem]:
    multiplication_items = []
    enabled = True

    for instruction_item, _ in re.findall(DO_DONT_MUL_REGEX, input_string):  # _ for the second capture group we do not care about
        if instruction_item == "do()":
            enabled = True
        elif instruction_item == "don't()":
            enabled = False
        elif instruction_item.startswith("mul"):
            if enabled:
                multiplication_items.append(MultiplicationItem(instruction_item))
        else:
            raise RuntimeError(f"Unrecognized instruction item: {instruction_item}")

    return multiplication_items

