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
        print_result(1, '---')

    def run_part_two(self):
        print_result(2, '---')
