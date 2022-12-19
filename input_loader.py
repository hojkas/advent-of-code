import os
from exceptions import RunException


class InputLoader:
    def __init__(self, filepath):
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            raise RunException('File with name ' + filepath + ' does not exist.')
        self.filepath = filepath

    def _load_input_as_generator(self, separator, retype_int=False):
        pass

    def _load_input(self, separator, retype_int=False):
        with open(self.filepath, 'r') as f:
            full_input = f.read().split(separator)
        if retype_int:
            return [int(x) for x in full_input]
        else:
            return full_input

    def load_input_string_array(self, separator='\n'):
        return self._load_input(separator)

    def load_input_int_array(self, separator='\n'):
        return self._load_input(separator, True)

    def load_input_string_array_as_generator(self, separator='\n'):
        pass

    def load_input_int_array_as_generator(self, separator='\n'):
        pass
