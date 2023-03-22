from datetime import datetime


def timethis(func):
    def wrapper(*args, **kwargs):
        before = datetime.now()
        result = func(*args, **kwargs)
        after = datetime.now()
        print("[", after.strftime("%H:%M:%S"), "] '", func.__name__, "' took ", (after - before).total_seconds(),
              " seconds.", sep="")
        return result

    return wrapper
