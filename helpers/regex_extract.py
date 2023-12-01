import re

from lib.exceptions import RunException


def regex_extract(regex, string):
    match = re.search(regex, string)
    if match and len(match.groups()) > 0:
        return match.group(1)
    raise RunException("Regex '" + regex + "' failed to find match in '" + string + "'.")


def regex_extract_multiple(regex, string, number_of_groups):
    match = re.search(regex, string)
    if match and len(match.groups()) == number_of_groups:
        return [match.group(x + 1) for x in range(number_of_groups)]
    raise RunException("Regex '" + regex + "' failed to find match in '" + string + "' "
                       "or the number of matches was unexpected.")
