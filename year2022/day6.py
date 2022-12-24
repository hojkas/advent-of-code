import os
from abstract_day import AbstractDay
from exceptions import RunException
from helpers import CC
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
        sequence = self.input_loader.load_input()
        result = self.part_one(sequence)
        print_result(1, result)

    def run_part_two(self):
        sequence = self.input_loader.load_input()
        result = self.part_two(sequence)
        print_result(2, result)

    def part_generalized(self, sequence: str, length: int) -> int:
        last_chars = []
        for i, char in enumerate(sequence):
            last_chars.append(char)
            if len(last_chars) < length:
                continue
            last_chars_set = set(last_chars)
            if len(last_chars_set) == length:
                self.dbg("last chars:", last_chars)
                self.dbg("last chars set:", last_chars_set)
                return i + 1
            last_chars.pop(0)

        raise RunException('Sequence was supposed to be found.')

    def part_one(self, sequence: str) -> int:
        return self.part_generalized(sequence, 4)

    def part_two(self, sequence: str) -> int:
        return self.part_generalized(sequence, 14)
