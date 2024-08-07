from typing import Optional

from lib.abstract_day import AbstractDay
from helpers import InputLoader


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Optional[InputLoader] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        return "---"

    def run_part_two(self):
        return "---"
