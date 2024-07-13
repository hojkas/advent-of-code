from dataclasses import dataclass
from typing import Optional

from lib.abstract_day import AbstractDay
from helpers import InputLoader


class ValueHistory:
    def __init__(self, value_sequence: list[int]) -> None:
        self.value_history: list[int] = value_sequence
        self.increment_history: Optional[ValueHistory] = None

        if any(value_sequence):
            increments = []
            i = 0
            while i + 1 < len(value_sequence):
                increments.append(value_sequence[i + 1] - value_sequence[i])
                i += 1
            self.increment_history = ValueHistory(increments)

    def get_next_value(self) -> int:
        if self.increment_history:
            return self.value_history[-1] + self.increment_history.get_next_value()
        else:
            return self.value_history[-1]

    def get_previous_value(self) -> int:
        if self.increment_history:
            return self.value_history[0] - self.increment_history.get_previous_value()
        else:
            return self.value_history[0]


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        input_data = self.input_loader.load_input_array(item_separator="\n")
        value_histories = load_value_histories(input_data)
        result = sum([value_history.get_next_value() for value_history in value_histories])
        return result

    def run_part_two(self):
        input_data = self.input_loader.load_input_array(item_separator="\n")
        value_histories = load_value_histories(input_data)
        result = sum([value_history.get_previous_value() for value_history in value_histories])
        return result


def load_value_histories(input_data: list[str]) -> list[ValueHistory]:
    value_histories = []
    for input_line in input_data:
        value_sequence = [int(value) for value in input_line.split(" ")]  # if ValueError shutdown is fine
        value_histories.append(ValueHistory(value_sequence))
    return value_histories
