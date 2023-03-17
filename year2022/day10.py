import os
from typing import Union, List
from abstract_day import AbstractDay
from exceptions import RunException
from helpers import CC
from input_loader import InputLoader


def print_result(part, result):
    filename = os.path.basename(__file__).split('.')[0]
    print('[', filename, '] ', CC.GREEN, 'Result of part ', part, CC.NC, ': ', result, sep='')


class LastInstructionException(Exception):
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


def part_one(input_array, cycle_breakpoints, stop_at):
    pc = Computer(input_array)
    cycle_sum = 0
    while True:
        if pc.cycle in cycle_breakpoints:
            cycle_sum += pc.signal_strenght()
        if pc.cycle == stop_at:
            return cycle_sum
        pc.run_next()


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
        result = part_one(input_array, [20, 60, 100, 140, 180, 220], 220)
        print_result(1, result)

    def run_part_two(self):
        print_result(2, '---')
