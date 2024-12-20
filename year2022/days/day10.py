from typing import Union, List

from lib.abstract_day import AbstractDay
from lib.exceptions import RunException
from helpers.input_loader import InputLoader


class LastInstructionException(RunException):
    pass


class Computer:
    def __init__(self, instructions):
        self.x = 1
        self.cycle = 1
        self.instructions = instructions
        self.instructions_index = 0
        self.next_addx_value = 0
        self.next_function = self._get_next_function()

    def _get_next_instruction_string(self) -> List[str]:
        try:
            instruction = self.instructions[self.instructions_index].split(" ")
        except IndexError:
            raise LastInstructionException()
        self.instructions_index += 1
        return instruction

    def _get_next_function(self):
        instruction = self._get_next_instruction_string()
        if instruction[0] == "noop":
            return self._noop
        elif instruction[0] == "addx":
            self.next_addx_value = int(instruction[1])
            return self._addx_cycle_one
        raise RunException("Unexpected value of instruction")

    def _noop(self):
        self.next_function = self._get_next_function()
        self.cycle += 1

    def _addx_cycle_one(self):
        self.next_function = self._addx_cycle_two
        self.cycle += 1

    def _addx_cycle_two(self):
        self.x += self.next_addx_value
        self.next_addx_value = 0
        self.next_function = self._get_next_function()
        self.cycle += 1

    def run_next(self):
        self.next_function()

    def signal_strenght(self):
        return self.cycle * self.x

    def sprite_in_position(self, position):
        if abs(position - self.x) <= 1:
            return True
        return False


def part_one(input_array, cycle_breakpoints, stop_at):
    pc = Computer(input_array)
    cycle_sum = 0
    while True:
        if pc.cycle in cycle_breakpoints:
            cycle_sum += pc.signal_strenght()
        if pc.cycle == stop_at:
            return cycle_sum
        pc.run_next()


def part_two(input_array, display_lenght, display_height):
    pc = Computer(input_array)
    while True:
        if pc.sprite_in_position(pc.cycle % display_lenght - 1):
            print("#", end="")
        else:
            print(".", end="")
        if pc.cycle % display_lenght == 0:
            print()
        if pc.cycle == display_lenght * display_height:
            return
        pc.run_next()


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_array = self.input_loader.load_input_array("\n")
        result = part_one(input_array, [20, 60, 100, 140, 180, 220], 220)
        return result

    def run_part_two(self):
        input_array = self.input_loader.load_input_array("\n")
        part_two(input_array, 40, 6)
        return 'See terminal'
