from lib.db_functions import ScopedSession
from lib.models import Address, User
from lib.threadmeister import threadmeister

# This has failed in the past with updates. Seems very inconsistent.


def main(total: int):
    """commits each record with a new SQLAlchemy scoped Session per commit, using threads;
    uses the ORM's "merge" method"""

    def save(i):
        with ScopedSession() as sess:
            user = User(id=i, name=f"name_{i}")
            address = Address(id=i, street_address=f"{i} Foo St.", user=user)
            sess.merge(user)
            sess.merge(address)
            sess.commit()

        return

    threadmeister(total, save)
    return
