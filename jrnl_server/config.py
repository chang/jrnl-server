import os
import jrnl


class Config:

    # Name of the author to be used in page headers.
    NAME = 'Eric'

    # Text displayed below page title.
    SUBTITLE = 'Hello world!'

    # Path to .jrnl_config.
    CONFIG_PATH = os.path.join(os.environ['HOME'], '.jrnl_config')

    # Name of the journal to render.
    JOURNAL_NAME = 'default'

    # Colors to give tags. Can be either Bulma colors or hexadecimal colors.
    TAG_COLORS = {
        '@tag': 'info',
    }

    @property
    def jrnl_config(self):
        config = jrnl.util.load_and_fix_json(self.CONFIG_PATH)
        journal_config = config['journals'].get(self.JOURNAL_NAME)
        config.update(journal_config)
        return config


conf = Config()
