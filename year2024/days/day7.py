import itertools
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Generator

from lib.abstract_day import AbstractDay
from helpers import InputLoader


class Operation(Enum):
    ADD = 0
    MUL = 1
    CONCAT = 2

    def exec(self, item_a: int, item_b: int) -> int:
        if self == Operation.ADD:
            return item_a + item_b
        elif self == Operation.MUL:
            return item_a * item_b
        elif self == Operation.CONCAT:
            return int(f"{item_a}{item_b}")
        else:
            raise ValueError("Operation not supported")

    @classmethod
    def create_possible_combinations(cls, n: int, exclude_concat: bool) -> Generator[list['Operation'], None, None]:
        if exclude_concat:
            return itertools.product([Operation.ADD, Operation.MUL], repeat=n)
        return itertools.product([Operation.ADD, Operation.CONCAT, Operation.MUL], repeat=n)


@dataclass
class Equation:
    result: int
    numbers: list[int]

    def is_solvable(self, exclude_concat: bool) -> bool:
        for operation_combo in Operation.create_possible_combinations(len(self.numbers) - 1, exclude_concat=exclude_concat):
            actual_result = self.numbers[0]
            for number, operation in zip(self.numbers[1:], operation_combo):
                actual_result = operation.exec(actual_result, number)
            if actual_result == self.result:
                return True
        return False


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_array = self.input_loader.load_input_array(item_separator="\n")
        equations = load_equations_from_input(input_array)
        return sum(equation.result for equation in equations if equation.is_solvable(exclude_concat=True))

    def run_part_two(self):
        input_array = self.input_loader.load_input_array(item_separator="\n")
        equations = load_equations_from_input(input_array)
        return sum(equation.result for equation in equations if equation.is_solvable(exclude_concat=False))


def load_equations_from_input(input_array: list[str]) -> list[Equation]:
    equations = []
    for line in input_array:
        raw_result, raw_numbers = line.split(": ")
        equation = Equation(int(raw_result), [])
        for raw_number in raw_numbers.split(" "):
            equation.numbers.append(int(raw_number))
        equations.append(equation)
    return equations
