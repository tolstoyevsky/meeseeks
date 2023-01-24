"""Module contains models definition. """

from gino import Gino

DB = Gino()


class User(DB.Model):  # pylint: disable=too-few-public-methods
    """User model definition. """

    __tablename__ = 'users'

    user_id = DB.Column(DB.String, primary_key=True)
    name = DB.Column(DB.String, nullable=False)
    birth_date = DB.Column(DB.DATE, nullable=True)
    fwd = DB.Column(DB.DATE, nullable=True)
