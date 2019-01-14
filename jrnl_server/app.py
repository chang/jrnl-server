import datetime
import json

from flask import Flask
import flask
import flask_login

from jrnl_server.config import conf
from jrnl_server.login import DummyUser
from jrnl_server.helpers import reload_on_change, populate_config
from jrnl_server.wrappers import JournalWrapper, EntryWrapper, NoEntryError



app = Flask(__name__)
app.secret_key = conf.SECRET
populate_config(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'

journal = JournalWrapper()



@login_manager.user_loader
def user_loader(_):
    return DummyUser()


@app.route('/login', methods=['GET', 'POST'])
def login():
    # import ipdb; ipdb.set_trace()
    if flask.request.method == 'GET':
        return flask.render_template('login.html', bad_login=False)

    if flask.request.method == 'POST':
        if flask.request.form['password'] == conf.PASSWORD:
            user = DummyUser()
            flask_login.login_user(user)
            return flask.redirect('/')
        else:
            return flask.render_template('login.html', bad_login=True)


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect('/login')


@app.route('/')
@flask_login.login_required
# @reload_on_change(journal)
def index():
    context = {
        'entry_links': journal.get_entry_links()
    }
    return flask.render_template('index.html', **context)


@app.route('/entry/<path:date>')
# @reload_on_change(journal)
@flask_login.login_required
def entry(date):
    try:
        parsed_entry = EntryWrapper(journal.get_entry(date))
        context = {
            'parsed_entry': parsed_entry,
        }
    except NoEntryError:
        context = {
            'date': date,
            'title': 'Oops.',
            'body_paragraphs': ["There's no entry for this day!"],
            'num_words': '?',
        }

    return flask.render_template('entry.html', **context)


@app.route('/stats')
@reload_on_change(journal)
def stats():
    options = {
        'tag_stats': journal.tag_stats,
        'num_entries': len(journal.journal.entries),
        'num_words': journal.word_count(),
        'num_tags': len(journal.tag_stats),
    }
    return flask.render_template('stats.html', **options)
