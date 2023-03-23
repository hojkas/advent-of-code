class CommandlineColors:
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    WHITE = "\033[0;37m"
    NC = "\033[0m"
    NOCOLOR = "\033[0m"


CC = CommandlineColors()


def pretty_print_result(year, day, part, result):
    print('[', year, '-day', day, '] ', CC.GREEN, 'Result of part ', part, CC.NC, ': ', result, sep='')