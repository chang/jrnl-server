from functools import wraps
import datetime
import json

from flask import Flask
import flask

from jrnl_server.wrappers import JournalWrapper, EntryWrapper, NoEntryError


app = Flask(__name__)

journal = JournalWrapper()


def reload_journal_on_change(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        journal.reload_if_changed()
        return func(*args, **kwargs)
    return decorated


@app.route('/')
@reload_journal_on_change
def index():
    entry_links = journal.get_entry_links()
    return flask.render_template('index.html', entry_links=entry_links)


@app.route('/entry/<path:date>')
@reload_journal_on_change
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
@reload_journal_on_change
def stats():
    options = {
        'tag_stats': journal.tag_stats,
        'num_entries': len(journal.journal.entries),
        'num_words': journal.word_count(),
        'num_tags': len(journal.tag_stats),
    }
    return flask.render_template('stats.html', **options)
