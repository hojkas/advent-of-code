import os
from typing import Union
from abstract_day import AbstractDay
from exceptions import RunException
from old_helpers import CC
from input_loader import InputLoader
import re


class Crate:
    def __init__(self, name):
        self.name = name.replace('[', '').replace(']', '')


class CrateStack:
    def __init__(self):
        self.stack = []

    def add(self, crate: Crate):
        self.stack.append(crate)

    def take(self) -> Crate:
        return self.stack.pop()

    def read_top(self) -> Crate:
        return self.stack[-1]

    def print_stack(self):
        for crate in self.stack:
            print(' [', crate.name, ']', sep='', end='')
        print('')


class CratePile:
    def __init__(self, crate_pile_string):
        crate_pile_string_split = crate_pile_string.split('\n')
        crate_stack_positions = {}
        self.crate_stacks = {}
        stack_pile_legend = crate_pile_string_split[-1]

        for position, char in enumerate(stack_pile_legend):
            if char.isnumeric():
                num = int(char)
                crate_stack_positions[num] = position
                self.crate_stacks[num] = CrateStack()

        for crate_pile_line in crate_pile_string_split[-2::-1]:
            for stack_number, position in crate_stack_positions.items():
                try:
                    if crate_pile_line[position].isalpha():
                        self.crate_stacks[stack_number].add(Crate(crate_pile_line[position]))
                except IndexError:
                    continue  # some strings are not long enough because last stack has no crates

    def move_crates_basic(self, how_many, from_x, to_x):
        for i in range(how_many):
            self.move_crate(from_x, to_x)

    def move_crate(self, from_x, to_x):
        moved_crate = self.crate_stacks[from_x].take()
        self.crate_stacks[to_x].add(moved_crate)

    def move_crates_multiple(self, how_many, from_x, to_x):
        crates_to_move = []
        for i in range(how_many):
            crates_to_move.append(self.crate_stacks[from_x].take())
        for crate in crates_to_move[::-1]:
            self.crate_stacks[to_x].add(crate)

    def print_all_stacks(self):
        for stack_number, stack in self.crate_stacks.items():
            print(stack_number, end='')
            stack.print_stack()

    def get_top_crates_string(self):
        res = ''
        for _, stack in sorted(self.crate_stacks.items()):  # sort to ensure the order
            res += stack.read_top().name
        return res


def part_generalized(string_instructions: str, crate_pile: CratePile, move_multiple_at_once: bool) -> str:
    instruction_regex = r"move (\d+) from (\d+) to (\d+)"
    for instruction_line in string_instructions.split('\n'):
        extracted_numbers = re.search(instruction_regex, instruction_line)
        if not extracted_numbers or len(extracted_numbers.groups()) != 3:
            raise RunException('Didnt find exactly 3 numbers in instruction line ' + instruction_line)
        move_x, from_x, to_x = (int(x) for x in extracted_numbers.groups())
        if move_multiple_at_once:
            crate_pile.move_crates_multiple(move_x, from_x, to_x)
        else:
            crate_pile.move_crates_basic(move_x, from_x, to_x)
    return crate_pile.get_top_crates_string()


def part_one(string_instructions: str, crate_pile: CratePile) -> str:
    return part_generalized(string_instructions, crate_pile, False)


def part_two(string_instructions: str, crate_pile: CratePile) -> str:
    return part_generalized(string_instructions, crate_pile, True)


def print_result(part, result):
    filename = os.path.basename(__file__).split('.')[0]
    print('[', filename, '] ', CC.GREEN, 'Result of part ', part, CC.NC, ': ', result, sep='')


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        configuration, instructions = self.input_loader.load_input_array(item_separator='\n\n')
        crate_pile = CratePile(configuration)
        result = part_one(instructions, crate_pile)
        print_result(1, result)

    def run_part_two(self):
        configuration, instructions = self.input_loader.load_input_array(item_separator='\n\n')
        crate_pile = CratePile(configuration)
        result = part_two(instructions, crate_pile)
        print_result(2, result)
