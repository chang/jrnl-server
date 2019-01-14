import logging
import os
from functools import wraps
from timeit import default_timer

from jrnl_server.config import conf


def reload_on_change(journal):
    def intermediate_decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            journal.reload_if_changed()
            return func(*args, **kwargs)
        return decorated
    return intermediate_decorator


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



def get_link_title(link):
    """Given a URL, return its title.

    If the title doesn't exist in the cache, asynchronously populate it so it's
    available on the next pageload.
    """
    from threading import Thread
    import requests
    import yaml
    from lxml.html import fromstring

    CACHE_PATH = '/tmp/jrnl_links.yaml'
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'r') as fp:
            cache = yaml.load(fp)
    else:
        cache = {}


    def get_title(link):
        RANDOM_STRING = 'asdfjsafieowjfklanwknfasdlfvzxcvxz'
        try:
            response = requests.get(link, headers={'User-Agent': RANDOM_STRING})
            tree = fromstring(response.content)
            title = tree.findtext('.//title')
            return title
        except Exception as e:
            logging.warning('Failed to GET: "{}"'.format(link))
            logging.warning(e)
            raise e


    def write_title_to_cache(link):
        cache[link] = get_title(link)
        with open(CACHE_PATH, 'w') as fp:
            fp.write(yaml.dump(cache, default_flow_style=False))


    if link in cache:
        return cache[link]
    else:
        thread = Thread(target=write_title_to_cache, kwargs={'link': link})
        thread.start()
        return link


def time_function(func):
    def decorated(*args, **kwargs):
        t0 = default_timer()
        result = func(*args, **kwargs)
        t1 = default_timer()
        elapsed = t1 - t0
        print('Function "{}": {}s'.format(func.__name__, elapsed))
        return result
    return decorated


def populate_config(app):
    app.config['NAME'] = conf.NAME
    app.config['SUBTITLE'] = conf.SUBTITLE
