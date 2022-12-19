from helpers import CC, ArgumentException, ArgumentParser
from scaffold_constructor import ScaffoldConstructor
from runner import Runner
from exceptions import RunException, ConstructionException


def main():
    try:
        args = ArgumentParser().parse()
        if args.run:
            Runner.run(args.day, args.year, args.part, args.debug)
        else:
            ScaffoldConstructor.construct(args.day, args.year, args.debug)

    except ArgumentException as ex:
        print(CC.RED, 'Argument Error: ', CC.NC, ex, sep='')
    except ConstructionException as ex:
        print(CC.RED, 'Construction Error: ', CC.NC, ex, sep='')
    except RunException as ex:
        print(CC.RED, 'Run Error: ', CC.NC, ex, sep='')


if __name__ == '__main__':
    main()
