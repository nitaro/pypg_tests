from lib.db_functions import Session
from lib.models import Address, User

"""
Used autoflush=False and session.close() because otherwise I got:

/home/nitin/Desktop/smart_commit/tests/test_sa_static_session.py:18: SAWarning: Object of type <Address>
not in session, add operation along 'User.address' will not proceed (This warning originated from the
Session 'autoflush' process, which was invoked automatically in response to a user-initiated operation.

Consider using ``no_autoflush`` context manager if this warning happended while initializing objects.)"""


def main(total: int):
    """commits each record with a static SQLAlchemy Session;
    uses the ORM to first check if the items exist in the db"""

    sess = Session(autoflush=False)
    for i in range(total):
        _usr = sess.query(User).filter(User.id == i).first()
        user = _usr or User(id=i, name=f"name_{i}")
        _addrs = (
            sess.query(Address).filter(Address.id == i, Address.user == user).first()
        )
        addrs = _addrs or Address(id=i, street_address=f"{i} Foo St.", user=user)
        sess.add(user)
        sess.add(addrs)

    sess.commit()
    sess.close()

    return
