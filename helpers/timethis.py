from datetime import datetime


def timethis(func):
    def inner1(*args, **kwargs):
        before = datetime.now()
        func(*args, **kwargs)
        after = datetime.now()
        print("[", after, "] '", func.__name__, "' took ", after - before, sep="")

    return inner1
