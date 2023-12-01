from lib.exceptions import RunException, ConstructionException, ArgumentException
from helpers import CC
from lib.runner import Runner
from lib.scaffold_constructor import ScaffoldConstructor
from lib.argument_parser import ArgumentParser


def main():
    try:
        args = ArgumentParser().parse()
        if args.run:
            Runner.run(args.day, args.year, args.part, args.timeit)
        else:
            ScaffoldConstructor.construct(args.day, args.year)

    except ArgumentException as ex:
        print(CC.RED, 'Argument Error: ', CC.NC, ex, sep='')
    except ConstructionException as ex:
        print(CC.RED, 'Construction Error: ', CC.NC, ex, sep='')
    except RunException as ex:
        print(CC.RED, 'Run Error: ', CC.NC, ex, sep='')


if __name__ == '__main__':
    main()
