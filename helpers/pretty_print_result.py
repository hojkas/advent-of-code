from helpers import CC


def pretty_print_result(year, day, part, result):
    print('[', year, '-day', day, '] ', CC.GREEN, 'Result of part ', part, CC.NC, ': ', result, sep='')
