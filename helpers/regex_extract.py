import re

from exceptions import RunException


def regex_extract(regex, string):
    match = re.search(regex, string)
    if match and len(match.groups()) > 0:
        return match.group(1)
    raise RunException("Regex '" + regex + "' failed to find match in '" + string + "'.")
