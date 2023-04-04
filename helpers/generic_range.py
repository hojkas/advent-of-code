from exceptions import RunException


class Range:
    def __init__(self, start, end):
        if start > end:
            raise RunException(f"Start {start} cannot be bigger than end {end}")
        self.start = start
        self.end = end

    def __str__(self):
        return f"[{self.start};{self.end}]"

    def __repr__(self):
        return f"[{self.start};{self.end}]"