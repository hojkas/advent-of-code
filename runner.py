from importlib import import_module
from abstract_day import AbstractDay
from exceptions import RunException
from input_loader import InputLoader


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
        pass

    @staticmethod
    def run(day, year, part, debug):
        runner = Runner._import_day_runner(day, year)
        runner.add_input_loader(Runner._construct_input_loader(day, year))
        runner.use_debug(debug)
        if part == 0 or part == 1:
            runner.run_part_one()
        if part == 0 or part == 2:
            runner.run_part_two()
