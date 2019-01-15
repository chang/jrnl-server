import os
import re
import logging

import flask
import jrnl

from jrnl_server.config import conf
from jrnl_server.elements import HTMLTag
from jrnl_server.helpers import get_day_with_suffix


LINK_REGEX = re.compile(r'https?:\/\/[www]?.+')

ITALIC_REGEX = re.compile(r'\*[a-zA-Z ]+\*')


class NoEntryError(Exception):
    pass


class JournalWrapper:

    def __init__(self):
        self._load_journal()

    def _load_journal(self):
        journal = jrnl.Journal.Journal(journal_name=conf.JOURNAL_NAME, **conf.jrnl_config)
        journal.open()
        self.journal = journal
        self.journal_dict = self.make_journal_dict(self.journal)
        self._modified_time = self._get_modified_time()

    def get_entry(self, date):
        # TODO: Do some input validation here.
        try:
            return self.journal_dict[date]
        except KeyError as e:
            msg = f'Attempted to access date with no entry: "{date}"'
            logging.warning(msg)
            raise NoEntryError(msg)

    def _get_modified_time(self):
        journal_path = conf.jrnl_config['journal']
        return os.stat(journal_path).st_mtime

    def reload_if_changed(self):
        modified_time = self._get_modified_time()
        if not self._modified_time == modified_time:
            print('Journal modified. Reloading.')
            self._load_journal()

    @property
    def entries(self):
        return self.journal.entries

    def word_count(self):
        return sum([EntryWrapper(e).word_count for e in self.journal.entries])

    def make_journal_dict(self, journal):
        journal_dict = {}
        for entry in journal.entries:
            dt = entry.date
            date_str = f'{dt.year}/{dt.month}/{dt.day}'
            journal_dict[date_str] = entry
        return journal_dict

    def get_entry_links(self):
        entry_links = []
        for date_str, entry in self.journal_dict.items():
            entry_name = f'<strong>{date_str}</strong>: {entry.title}'
            entry_link = f'entry/{date_str}'
            parsed_entry = EntryWrapper(entry)
            el = (entry_name, entry_link, parsed_entry)
            entry_links.append(el)
        # Do we need to sort this first? No guarantee of ordering in a dict...
        return reversed(entry_links)

    @property
    def tag_stats(self):
        """A list of tuples with the form: [(tag, n)]."""
        tag_list_count_first = list(jrnl.exporters.get_tags_count(self.journal))
        tag_list_count_first = sorted(tag_list_count_first, reverse=True)
        tag_list = [HTMLTag(tag).count_pill(n) for n, tag in tag_list_count_first]
        return tag_list


class EntryWrapper:
    def __init__(self, entry):
        self.entry = entry

    @property
    def title(self):
        return self.entry.title

    @property
    def tags(self):
        unique_tags = list(set(self.entry.tags))
        return sorted(unique_tags)

    @property
    def is_starred(self):
        return self.entry.starred

    def html_tags(self):
        return [HTMLTag(t).pill() for t in self.tags]

    def html_word_count(self):
        return f'<span class="tag is-dark is-rounded">{self.word_count}</span>'

    @property
    def date(self):
        raw_date = self.entry.date
        day, suffix = get_day_with_suffix(raw_date.day)
        date_str = raw_date.strftime(f'%A, %B {day}<sup>{suffix}</sup> %Y')
        return date_str

    @property
    def word_count(self):
        return len([w for w in self.entry.body.split(" ") if w])

    def _render_lists(self, body):
        def is_list_item(p):
            return p.strip().startswith('- ')

        paragraphs = body.split('\n')
        rendered, unordered_list = [], []
        for i, p in enumerate(paragraphs):
            if is_list_item(p):
                unordered_list.append(p.lstrip('- '))
                end_of_list = (i == len(paragraphs) - 1) or not is_list_item(paragraphs[i + 1])
                if end_of_list:
                    html_list = flask.render_template('_unordered_list.html', items=unordered_list)
                    rendered.append(html_list)
                    unordered_list = []
            else:
                rendered.append(p)

        return '\n'.join(rendered)

    def _render_italics(self, paragraph):
        for match in ITALIC_REGEX.findall(paragraph):
            assert match[0] == '*' and match[-1] == '*'
            match_without_asterisks = match[1:-1]
            html_italic = '<span class="is-italic">{}</span>'.format(match_without_asterisks)
            paragraph = paragraph.replace(match, html_italic)
        return paragraph

    def _render_links(self, paragraph):
        matches = LINK_REGEX.findall(paragraph)
        for match in matches:
            html_link = '<a href="{0}">{0}</a>'.format(match)
            paragraph = paragraph.replace(match, html_link)
        return paragraph

    def _render_tags(self, paragraph):
        # Render tags in the body of the journal entry.
        for tag in self.tags:
            paragraph = paragraph.replace(tag, HTMLTag(tag).text())
        return paragraph

    @property
    def body_paragraphs(self):
        body = self.entry.body
        body = self._render_lists(body)
        body = self._render_tags(body)
        body = self._render_links(body)
        body = self._render_italics(body)
        paragraphs = body.split('\n')
        return paragraphs
