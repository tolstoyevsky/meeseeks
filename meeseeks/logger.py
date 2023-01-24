"""Module contains logging configuration. """

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s; %(levelname)s; %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# Turn off the annoying gino SQL echo message
logging.getLogger('gino.engine._SAEngine').setLevel(logging.ERROR)

LOGGER = logging.getLogger('meeseeks-core')
