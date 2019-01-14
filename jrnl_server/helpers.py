from timeit import default_timer


def get_day_with_suffix(day):
    """
    Returns:
        (day, suffix): (TUPLE[STR, STR])
    """
    assert isinstance(day, int) and 0 < day <= 31
    SUFFIXES = {
        1: 'st',
        2: 'nd',
        3: 'rd',
        4: 'th',
        21: 'st',
        22: 'nd',
        23: 'rd',
        24: 'th',
        31: 'st',
    }
    suffix_day = day
    while True:
        if suffix_day in SUFFIXES:
            suffix = SUFFIXES[suffix_day]
            return (str(day), suffix)
        suffix_day -= 1


def time_function(func):
    def decorated(*args, **kwargs):
        t0 = default_timer()
        result = func(*args, **kwargs)
        t1 = default_timer()
        elapsed = t1 - t0
        print('Function "{}": {}s'.format(func.__name__, elapsed))
        return result
    return decorated
