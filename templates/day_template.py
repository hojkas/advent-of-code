from abstract_day import AbstractDay
from exceptions import RunException


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader = None
        self.debug = False

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def use_debug(self, use_debug=False):
        self.debug = use_debug

    def run_part_one(self):
        pass

    def run_part_two(self):
        pass
