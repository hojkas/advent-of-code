import os
from typing import Union
from abstract_day import AbstractDay
from exceptions import RunException
from old_helpers import CC
from input_loader import InputLoader


def print_result(part, result):
    filename = os.path.basename(__file__).split('.')[0]
    print('[', filename, '] ', CC.GREEN, 'Result of part ', part, CC.NC, ': ', result, sep='')


class DayRunner(AbstractDay):
    def __init__(self):
        self.input_loader: Union[InputLoader, None] = None

    def add_input_loader(self, input_loader):
        self.input_loader = input_loader

    def run_part_one(self):
        print_result(1, '---')

    def run_part_two(self):
        print_result(2, '---')
