import flask_login

from jrnl_server.config import conf


class DummyUser(flask_login.UserMixin):

    @property
    def id(self):
        return conf.NAME
