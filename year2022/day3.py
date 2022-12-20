import os
from abstract_day import AbstractDay
from exceptions import RunException
from helpers import CC
from input_loader import InputLoader


def print_result(part, result):
    filename = os.path.basename(__file__).split('.')[0]
    print('[', filename, '] ', CC.GREEN, 'Result of part ', part, CC.NC, ': ', result, sep='')


def get_item_priority(letter):
    ord_value = ord(letter)
    if ord('a') <= ord_value <= ord('z'):
        # range 1 to 26
        return ord_value - ord('a') + 1
    if ord('A') <= ord_value <= ord('Z'):
        # range 27 to 52
        return ord_value - ord('A') + 27
    raise RunException('This point should not be reached')


def split_backpack(backpack_line):
    if len(backpack_line) % 2 != 0:
        raise RunException('Line has odd count, something is wrong. ' + backpack_line)
    split_point = int(len(backpack_line) / 2)
    return backpack_line[:split_point], backpack_line[split_point:]


def find_duplicate(box_a, box_b):
    set_a = set(box_a)
    set_b = set(box_b)
    for char in set_a:
        if char in set_b:
            return char
    raise RunException('At least one item should have been found')


def part_one(input_array):
    priority_sum = 0
    for backpack in input_array:
        compartment_a, compartment_b = split_backpack(backpack)
        duplicate_item = find_duplicate(compartment_a, compartment_b)
        priority_sum += get_item_priority(duplicate_item)
    return priority_sum


def group_by_three(iterable):
    a = iter(iterable)
    return zip(a, a, a)


def find_common_elements(elf1, elf2, elf3):
    set1 = set(elf1)
    set2 = set(elf2)
    set3 = set(elf3)
    return set1.intersection(set2).intersection(set3)


def part_two(input_array):
    priority_sum = 0
    for elf_group in group_by_three(input_array):
        common = find_common_elements(elf_group[0], elf_group[1], elf_group[2])
        if len(common) != 1:
            raise RunException('There should be exactly one common element, something is wrong.')
        (single_common, ) = common
        priority_sum += get_item_priority(single_common)
    return priority_sum


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: InputLoader | None = None
        self.debug_mode = False

    def dbg(self, *args, **kwargs):
        if self.debug_mode:
            print(*args, **kwargs)

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def use_debug(self, use_debug=False):
        self.debug_mode = use_debug

    def run_part_one(self):
        input_array = self.input_loader.load_input_array(item_separator='\n')
        result = part_one(input_array)
        print_result(1, result)

    def run_part_two(self):
        input_array = self.input_loader.load_input_array(item_separator='\n')
        result = part_two(input_array)
        print_result(2, result)
