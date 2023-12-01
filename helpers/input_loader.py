import os
from lib.exceptions import RunException


class InputLoader:
    def __init__(self, filepath):
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            raise RunException('Input file with name ' + str(filepath) + ' does not exist.')
        self.filepath = filepath

    def load_input_as_generator(self, item_separator, retype_int=False):
        raise RunException('Load input function not yet implemented')

    def load_input(self):
        with open(self.filepath, 'r') as f:
            return f.read()

    def load_input_array(self, item_separator, retype_item_to_int=False):
        with open(self.filepath, 'r') as f:
            full_input = f.read().strip().split(item_separator)
        if retype_item_to_int:
            return [int(x) for x in full_input]
        else:
            return full_input

    def load_input_array_of_array(self, subarray_separator, item_separator, retype_item_to_int=False):
        with open(self.filepath, 'r') as f:
            full_input = f.read().strip().split(subarray_separator)
        if retype_item_to_int:
            return [[int(x) for x in y.split(item_separator)] for y in full_input]
        else:
            return [y.split(item_separator) for y in full_input]
