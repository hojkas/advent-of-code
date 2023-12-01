from typing import Union
from lib.abstract_day import AbstractDay
from helpers.input_loader import InputLoader


def _part_one(input_array):
    best_calorie_count = 0
    for elf_array in input_array:
        elf_sum = 0
        for calorie_item in elf_array:
            elf_sum += calorie_item
        if elf_sum > best_calorie_count:
            best_calorie_count = elf_sum
    return best_calorie_count


def _part_two(input_array):
    calorie_counts = []
    for elf_array in input_array:
        elf_sum = 0
        for calorie_item in elf_array:
            elf_sum += calorie_item
        calorie_counts.append(elf_sum)

    calorie_counts.sort(reverse=True)
    return calorie_counts[0] + calorie_counts[1] + calorie_counts[2]


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_array = self.input_loader.load_input_array_of_array(subarray_separator='\n\n',
                                                                  item_separator='\n', retype_item_to_int=True)
        return _part_one(input_array)

    def run_part_two(self):
        input_array = self.input_loader.load_input_array_of_array(subarray_separator='\n\n',
                                                                  item_separator='\n', retype_item_to_int=True)
        return _part_two(input_array)
