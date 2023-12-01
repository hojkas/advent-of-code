import argparse

from lib.exceptions import ArgumentException
from config import Config


class ArgumentParser:
    __slots__ = ['day', 'year', 'construct', 'run', 'part', 'timeit']

    def parse(self):
        parser = argparse.ArgumentParser(description='AOC custom runner')
        parser.add_argument('--cli', action='store_true', default=False,
                            help='CLI mode asks for an action and day via CLI. Ignores any other flags.')
        parser.add_argument('-d', '--day', dest='day', type=int, help='Day number')
        parser.add_argument('-y', '--year', dest='year', type=int, help='Year number')
        parser.add_argument('-c', '--construct', dest='construct', action='store_true', default=False,
                            help='When flag is present, create the day files instead.')
        parser.add_argument('-r', '--run', dest='run', action='store_true', default=False,
                            help='Run selected day.')
        parser.add_argument('-p', '--part', dest='part', default=0, type=int,
                            help='Part to run when running day. 0 = both, 1 = part 1, 2 = part 2.')
        parser.add_argument('-t', '--timeit', dest='timeit', default=False, action='store_true',
                            help='When set to true, parts of the day that are run will be timed.')

        parsed_args = parser.parse_args()
        self._assign_args(parsed_args)
        if parsed_args.cli:
            self._cli_override_args()
        self._validate()
        return self

    def _assign_args(self, args):
        config = Config()

        self.day = args.day
        self.year = args.year if args.year else config.default_year
        self.construct = args.construct
        self.run = args.run
        self.part = args.part
        self.timeit = args.timeit

    def _validate(self):
        if self.day < 1 or self.day > 25:
            raise ArgumentException('Day value needs to be <1,25>')
        if self.year < 2015:
            raise ArgumentException('Year value needs to be 2015 or bigger - sadly, no Advent of Code before that year')
        if self.construct == self.run:
            raise ArgumentException('One of the construct or run modes needs to be selected. Not both nor none of them')
        if self.part < 0 or self.part > 2:
            raise ArgumentException('Part needs to be a number <0,2>')

    def _cli_override_args(self):
        day = input('What day?\n')
        try:
            self.day = int(day)
        except ValueError:
            raise ArgumentException('Day needs to be integer')

        other = input('Any other changes to default? y/n (Blank for no)\n')
        if other != 'y':
            return

        year = input('Different year than the default ' + str(self.year) + '? (Blank for no change)\n')
        if year:
            try:
                self.year = int(year)
            except ValueError:
                raise ArgumentException('Year needs to be an integer.')

        construct = input('Construct mode? y/n (Blank for no)\n')
        if construct == 'y':
            self.construct = True
            self.run = False
        else:
            part = input('Which part to run? 0-2 (Leave blank for 0 = both)\n')
            part = part if part else 0
            try:
                self.part = int(part)
            except ValueError:
                raise ArgumentException('Part needs to be integer.')

            timeit = input('Should the part execution be timed? y/n (Blank for no)\n')
            self.timeit = True if timeit == 'y' else False
