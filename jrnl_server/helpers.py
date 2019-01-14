from functools import wraps
from timeit import default_timer

from jrnl_server.config import conf


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


def reload_on_change(journal):
    def intermediate_decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            journal.reload_if_changed()
            return func(*args, **kwargs)
        return decorated
    return intermediate_decorator


def populate_config(app):
    app.config['NAME'] = conf.NAME
    app.config['SUBTITLE'] = conf.SUBTITLE
