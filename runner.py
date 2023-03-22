from importlib import import_module
from abstract_day import AbstractDay
from exceptions import RunException
from input_loader import InputLoader
from os.path import sep
import pathlib


class Runner:
    @staticmethod
    def _import_day_runner(day, year) -> AbstractDay:
        try:
            module_name = 'year' + str(year) + '.day' + str(day)
            module = import_module(module_name)
            the_class = getattr(module, 'DayRunner')
            return the_class()
        except ModuleNotFoundError as e:
            raise RunException(e.msg)

    @staticmethod
    def _construct_input_loader(day, year) -> InputLoader:
        local_filepath = '.' + sep + 'year' + str(year) + sep + 'day' + str(day) + '_input'
        filepath = pathlib.Path(local_filepath).resolve()
        return InputLoader(filepath)

    @staticmethod
    def run(day, year, part):
        runner = Runner._import_day_runner(day, year)
        runner.add_input_loader(Runner._construct_input_loader(day, year))
        if part == 0 or part == 1:
            runner.run_part_one()
        if part == 0 or part == 2:
            runner.run_part_two()
