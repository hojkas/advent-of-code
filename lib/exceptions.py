class RunException(Exception):
    pass


class ConstructionException(RunException):
    pass


class ArgumentException(RunException):
    pass


class RegexNotFoundException(RunException):
    pass
