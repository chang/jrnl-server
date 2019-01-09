import os
import jrnl


def load_config():
    config = jrnl.util.load_and_fix_json(CONFIG_PATH)
    journal_config = config['journals'].get(JOURNAL_NAME)
    config.update(journal_config)
    return config


CONFIG_PATH = os.path.join(os.environ['HOME'], '.jrnl_config')

JOURNAL_NAME = 'default'

TAG_COLORS = {
    '@tag': 'info',
}

JRNL_CONFIG = load_config()
