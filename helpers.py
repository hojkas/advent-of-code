import argparse
import json


class CommandlineColors:
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    WHITE = "\033[0;37m"
    NC = "\033[0m"
    NOCOLOR = "\033[0m"


CC = CommandlineColors()


class Config:
    def __init__(self):
        with open('config.json', 'r') as f:
            self._config_json = json.load(f)

    def __getitem__(self, key):
        return self._config_json[key]

    def has_key(self, k):
        return k in self._config_json


class ArgumentException(Exception):
    pass


class ArgumentParser:
    __slots__ = ['day', 'year', 'construct', 'run', 'part', 'debug']

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
        parser.add_argument('-v', '--verbose', '--debug', dest='debug', action='store_true', default=False,
                            help='Write debug messages.')

        parsed_args = parser.parse_args()
        self._assign_args(parsed_args)
        if parsed_args.cli:
            self._cli_override_args()
        self._validate()
        self._debug_pretty_print()
        return self

    def _assign_args(self, args):
        config = Config()

        self.day = args.day
        self.year = args.year if args.year else config['default_year']
        self.construct = args.construct
        self.run = args.run
        self.part = args.part
        self.debug = args.debug

    def _validate(self):
        if self.day < 1 or self.day > 25:
            raise ArgumentException('Day value needs to be <1,25>')
        if self.year < 2015:
            raise ArgumentException('Year value needs to be 2015 or bigger - sadly, no Advent of Code before that year')
        if self.construct == self.run:
            raise ArgumentException('One of the construct or run modes needs to be selected. Not both nor none of them')
        if self.part < 0 or self.part > 2:
            raise ArgumentException('Part needs to be a number <0,2>')

    def _pretty_print(self):
        for key in self.__slots__:
            print(CC.YELLOW, key, CC.NC, ': ', getattr(self, key), sep='')
        print()

    def _debug_pretty_print(self):
        if self.debug:
            self._pretty_print()

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

        debug = input('Debug mode? y/n (Blank for no)\n')
        if debug == 'y':
            self.debug = True
