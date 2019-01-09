import os
import jrnl


class Config:
    CONFIG_PATH = os.path.join(os.environ['HOME'], '.jrnl_config')

    JOURNAL_NAME = 'default'

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
