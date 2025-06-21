from lib.db_functions import ScopedSession
from lib.models import Address, User
from lib.threadmeister import threadmeister

# This has failed in the past with updates. Seems very inconsistent.


def main(total: int):
    """commits each record with a new SQLAlchemy scoped Session per commit, using threads;
    uses the ORM to first check if the items exist in the db"""

    def save(i):
        with ScopedSession() as sess:
            _usr = sess.query(User).filter(User.id == i).first()
            user = _usr or User(id=i, name=f"name_{i}")
            _addrs = (
                sess.query(Address)
                .filter(Address.id == i, Address.user == user)
                .first()
            )
            addrs = _addrs or Address(id=i, street_address=f"{i} Foo St.", user=user)
            sess.add(user)
            sess.add(addrs)
            sess.commit()

        # sess.remove()  # ??? Should this be here?
        return

    threadmeister(total, save)
    return
