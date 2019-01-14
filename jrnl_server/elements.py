import os
from jrnl_server.config import conf


def _consistent_hash(string):
    # hash() offsets the hash values with each session for security
    return sum([ord(s) for s in string])


class HTMLTag:
    def __init__(self, tag):
        self.tag = tag

    def _render(self, template, **kwargs):
        color = conf.TAG_COLORS[self.tag] if self.tag in conf.TAG_COLORS else self._get_color()
        return template.format(color=color, tag=self.tag, **kwargs)

    def _get_color(self):
        BULMA_COLORS = (
            'primary',
            'info',
            'link',
            'success',
            'warning',
            'danger',
        )
        i = _consistent_hash(self.tag) % len(BULMA_COLORS)
        return BULMA_COLORS[i]

    def pill(self):
        return self._render('<span class="tag is-rounded is-{color}">{tag}</span>')

    def text(self):
        return self._render('<span class="has-text-{color} has-text-weight-semibold">{tag}</span>')

    def count_pill(self, n):
        return self._render(
            """
            <div class="tags has-addons">
                <a class="tag is-{color} is-medium">{tag}</a>
                <a class="tag is-dark is-medium">{n}</a>
            </div>
            """,
            n=n
        )
