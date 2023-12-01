import pathlib
from importlib import import_module
from os.path import sep

from helpers import pretty_print_result
from helpers import timethis
from helpers.input_loader import InputLoader
from lib.abstract_day import AbstractDay
from lib.exceptions import RunException


class Runner:
    @staticmethod
    def _import_day_runner(day, year) -> AbstractDay:
        try:
            module_name = 'year' + str(year) + '.days.day' + str(day)
            module = import_module(module_name)
            the_class = getattr(module, 'DayRunner')
            return the_class()
        except ModuleNotFoundError as e:
            raise RunException(e.msg)

    @staticmethod
    def _construct_input_loader(day, year) -> InputLoader:
        local_filepath = '.' + sep + 'year' + str(year) + sep + 'inputs' + sep + 'day' + str(day) + '_input'
        filepath = pathlib.Path(local_filepath).resolve()
        return InputLoader(filepath)

    @staticmethod
    def _run_with_conditioned_timing(func, timeit):
        if timeit:
            func = timethis(func)
        return func()

    @staticmethod
    def run(day, year, part, timeit):
        runner = Runner._import_day_runner(day, year)
        runner.add_input_loader(Runner._construct_input_loader(day, year))
        if part == 0 or part == 1:
            result = Runner._run_with_conditioned_timing(runner.run_part_one, timeit)
            pretty_print_result(year, day, 1, result)
        if part == 0 or part == 2:
            result = Runner._run_with_conditioned_timing(runner.run_part_two, timeit)
            pretty_print_result(year, day, 2, result)
