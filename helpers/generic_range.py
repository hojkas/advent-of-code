from exceptions import RunException


class Range:
    def __init__(self, start, end):
        if start > end:
            raise RunException(f"Start {start} cannot be bigger than end {end}")
        self.start = start
        self.end = end

    def __str__(self):
        return f"<{self.start};{self.end}>"

    def __repr__(self):
        return f"<{self.start};{self.end}>"

    def __iter__(self):
        return range(self.start, self.end + 1).__iter__()

    def __len__(self):
        return self.end - self.start + 1
