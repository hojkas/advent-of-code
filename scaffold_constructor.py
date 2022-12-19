import os
from os.path import sep
from shutil import copyfile
from exceptions import ConstructionException


class ScaffoldConstructor:
    @staticmethod
    def _scaffold_year(yeardir, debug):
        os.mkdir(yeardir)
        init_path = yeardir + sep + '__init__.py'
        with open(init_path, 'w'):
            pass
        template_readme_path = 'templates/year_readme_template.md'
        target_readme_path = yeardir + sep + 'README.md'
        copyfile(template_readme_path, target_readme_path)

    @staticmethod
    def _scaffold_day(yeardir, day, debug):
        input_path = yeardir + sep + 'day' + str(day) + '_input'
        template_day_path = 'templates/day_template.py'
        target_day_path = yeardir + sep + 'day' + str(day) + '.py'

        if os.path.exists(input_path):
            raise ConstructionException('Input file already exists.')
        if os.path.exists(target_day_path):
            raise ConstructionException('Day file already exists.')

        with open(input_path, 'w'):
            pass
        copyfile(template_day_path, target_day_path)

    @staticmethod
    def construct(day, year, debug):
        yeardir = os.curdir + sep + 'year' + str(year)
        if os.path.isdir(yeardir):
            ScaffoldConstructor._scaffold_day(yeardir, day, debug)
        elif not os.path.exists(yeardir):
            ScaffoldConstructor._scaffold_year(yeardir, debug)
            ScaffoldConstructor._scaffold_day(yeardir, day, debug)
        else:
            raise ConstructionException(yeardir + ' needs to be dir, not file.')
