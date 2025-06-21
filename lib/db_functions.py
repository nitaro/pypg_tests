# Basic SQLAlchemy connection stuff and some convenience functions.

import logging

from sqlalchemy import create_engine as _create_engine
from sqlalchemy import text as _text
from sqlalchemy.orm import scoped_session, sessionmaker

from .config import CONFIG
from .models import Address, Base, User

SA_LOGGER = logging.getLogger("sqlalchemy.engine")
SA_LOGGER.level = logging.DEBUG

Engine = _create_engine(
    f"postgresql://{CONFIG.DB_USER}:{CONFIG.DB_PASSWORD}@{CONFIG.DB_LOCATION}/{CONFIG.DB_NAME}"
)
Session = sessionmaker(bind=Engine)
ScopedSession = scoped_session(sessionmaker(bind=Engine))


def print_rows():
    """Prints User and Address rows to screen. This is for quickly verifying values."""

    with Session() as sess:
        usrs = sess.query(User).order_by(User.id).all()
        for usr in usrs:
            print(usr, usr.address, sep=",", flush=True)

    return


def create_tables():
    """Creates User and Address tables in the db."""

    Base.metadata.create_all(Engine)

    logging.info("created db")
    return


def count_rows():
    """Prints counts of User and Address tables.

    This to verify the correct numbers of items are in the db.
    Each should match .env's TOTAL_ITEMS.
    """

    with Session() as sess:
        addr = sess.query(Address).count()
        usr = sess.query(User).count()

    logging.info(f"count User/Address: {usr}, {addr}")
    return usr, addr


def drop_rows():
    """Drops all rows for User and Address tables.

    Resets the auto-increment for the primary key.
    This is used to clear the db between each test.
    """

    with Session() as sess:
        sess.execute(
            _text(
                """DELETE FROM address;
                DELETE FROM user_account;
                ALTER SEQUENCE address_id_seq RESTART WITH 1;
                ALTER SEQUENCE user_account_id_seq RESTART WITH 1;
                """
            )
        )

        sess.commit()

    logging.info("dropped rows")
    return
