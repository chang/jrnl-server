import datetime
import os

import flask_login

from jrnl_server.config import conf


class DummyUser(flask_login.UserMixin):

    @property
    def id(self):
        return conf.NAME


class FailedLoginLogger:
    MESSAGES = [
        'Incorrect login.',
        'Fat rodent, fat rodent, whatcha gonna do?',
        "Stinkin' squirrel.",
        'Think about squeaky box, now.',
        'Cut it out bb, this is getting you nowhere.',
        'Fatty.',
        "This stubborn-ass rodent just won't give up, huh...",
        "Don't you have some studying to do?",
    ]

    def __init__(self):
        self.log_path = os.path.join(os.environ['HOME'], 'failed_login_attempts')
        self._touch_file()

    def log_attempt(self, password):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = '[{}] Failed login: "{}"'.format(now, password)
        with open(self.log_path, 'a') as fp:
            fp.write('\n')
            fp.write(log_line)

    def get_failed_message(self):
        return self.MESSAGES[self.num_lines_before_reset % len(self.MESSAGES)]

    def _touch_file(self):
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w') as fp:
                fp.write('')

    def _read_lines(self):
        with open(self.log_path, 'r') as fp:
            return fp.readlines()

    @property
    def num_lines(self):
        return len(self._read_lines())

    @property
    def num_lines_before_reset(self):
        lines = self._read_lines()
        n = 0
        i = len(lines) - 1
        while 'reset' not in lines[i].lower() and i >= 0:
            n += 1
            i -= 1
        return n
