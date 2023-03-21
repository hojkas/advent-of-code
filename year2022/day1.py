import os
from abstract_day import AbstractDay
from exceptions import RunException
from old_helpers import CC
from input_loader import InputLoader


def print_result(part, result):
    filename = os.path.basename(__file__).split('.')[0]
    print('[', filename, '] ', CC.GREEN, 'Result of part ', part, CC.NC, ': ', result, sep='')


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
        input_array = self.input_loader.load_input_array_of_array(subarray_separator='\n\n',
                                                                  item_separator='\n', retype_item_to_int=True)
        result = self._part_one(input_array)
        print_result(1, result)

    def run_part_two(self):
        input_array = self.input_loader.load_input_array_of_array(subarray_separator='\n\n',
                                                                  item_separator='\n', retype_item_to_int=True)
        result = self._part_two(input_array)
        print_result(2, result)

    def _part_one(self, input_array):
        best_calorie_count = 0
        for elf_array in input_array:
            elf_sum = 0
            for calorie_item in elf_array:
                elf_sum += calorie_item
            if elf_sum > best_calorie_count:
                best_calorie_count = elf_sum
        return best_calorie_count

    def _part_two(self, input_array):
        calorie_counts = []
        for elf_array in input_array:
            elf_sum = 0
            for calorie_item in elf_array:
                elf_sum += calorie_item
            calorie_counts.append(elf_sum)

        calorie_counts.sort(reverse=True)
        return calorie_counts[0] + calorie_counts[1] + calorie_counts[2]
