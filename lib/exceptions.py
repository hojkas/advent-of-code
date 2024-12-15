class RunException(Exception):
    pass


class ConstructionException(RunException):
    pass


class ArgumentException(RunException):
    pass


class RegexNotFoundException(RunException):
    pass


class OutOfBoundsError(Exception):
    """
    To be raised when operation on two dimensional map reaches out of bounds.
    """
    pass
