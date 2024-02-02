import os
import logging

def config_logger(log_file):
    LOG_FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format=LOG_FORMAT, datefmt=DATE_FORMAT)

    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger(None).addHandler(console)

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = os.path.join(CURRENT_DIR, 'log')

config_logger(LOG_FILE)
