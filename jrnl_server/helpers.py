import jrnl

from jrnl_server.config import conf


def load_journal():
    journal = jrnl.Journal.Journal(journal_name=conf.JOURNAL_NAME, **conf.jrnl_config)
    journal.open()
    return journal


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
