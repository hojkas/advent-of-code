from typing import Union

from lib.abstract_day import AbstractDay
from helpers.input_loader import InputLoader


class ElfSection:
    def __init__(self, elf_string):
        start_string, end_string = elf_string.split('-')
        self.start = int(start_string)
        self.end = int(end_string)
        self.area_size = self.end - self.start + 1


def elf_area_is_included(bigger_elf: ElfSection, smaller_elf: ElfSection) -> bool:
    if smaller_elf.start >= bigger_elf.start and smaller_elf.end <= bigger_elf.end:
        return True
    return False


def one_elf_includes_other(elf1: ElfSection, elf2: ElfSection) -> bool:
    if elf1.area_size >= elf2.area_size:
        return elf_area_is_included(elf1, elf2)
    else:
        return elf_area_is_included(elf2, elf1)


def elves_overlap(elf1: ElfSection, elf2: ElfSection) -> bool:
    if elf1.end < elf2.start or elf1.start > elf2.end:
        return False
    return True


def part_one(input_array):
    fully_included = 0
    for elf_pair in input_array:
        elf1_string, elf2_string = elf_pair.split(',')
        elf1 = ElfSection(elf1_string)
        elf2 = ElfSection(elf2_string)
        if one_elf_includes_other(elf1, elf2):
            fully_included += 1
    return fully_included


def part_two(input_array):
    partially_overlap = 0
    for elf_pair in input_array:
        elf1_string, elf2_string = elf_pair.split(',')
        elf1 = ElfSection(elf1_string)
        elf2 = ElfSection(elf2_string)
        if elves_overlap(elf1, elf2):
            partially_overlap += 1
    return partially_overlap


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_array = self.input_loader.load_input_array(item_separator='\n')
        result = part_one(input_array)
        return result

    def run_part_two(self):
        input_array = self.input_loader.load_input_array(item_separator='\n')
        result = part_two(input_array)
        return result
