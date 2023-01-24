"""Module contains VoteOrDie application settings. """

from apps.vote_or_die.defaults import *  # pylint: disable=wildcard-import,unused-wildcard-import

load_dotenv()

RESPOND_TO_DM = os.getenv('RESPOND_TO_DM', '').lower() == 'true'
