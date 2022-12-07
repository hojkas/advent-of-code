from helpers import CC, ArgumentException, ArgumentParser
from day_constructor import DayConstructor, ConstructionException
from day_runner import DayRunner, RunException


def main():
    try:
        args = ArgumentParser().parse()
        if args.run:
            DayRunner.run(args.day, args.year, args.part, args.debug)
        else:
            DayConstructor.construct(args.day, args.year, args.debug)

    except ArgumentException as ex:
        print(CC.RED, 'Argument Error: ', CC.NC, ex, sep='')
    except ConstructionException as ex:
        print(CC.RED, 'Construction Error: ', CC.NC, ex, sep='')
    except RunException as ex:
        print(CC.RED, 'Run Error: ', CC.NC, ex, sep='')


if __name__ == '__main__':
    main()
