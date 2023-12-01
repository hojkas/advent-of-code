from typing import Union

from lib.abstract_day import AbstractDay
from lib.exceptions import RunException
from helpers.input_loader import InputLoader


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        sequence = self.input_loader.load_input()
        result = self.part_one(sequence)
        return result

    def run_part_two(self):
        sequence = self.input_loader.load_input()
        result = self.part_two(sequence)
        return result

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
