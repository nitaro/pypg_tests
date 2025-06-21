from lib.db_functions import Session
from lib.models import Address, User
from lib.threadmeister import threadmeister

"""
Have gotten this in the past:
ERROR:root:generated an exception: This session is provisioning a new connection;
concurrent operations are not permitted (Background on this error at: https://sqlalche.me/e/20/isce)
"""


def main(total: int):
    """commits each record with a static SQLAlchemy Session using threads;
    uses the ORM to first check if the items exist in the db"""

    def save(i, sess):
        _usr = sess.query(User).filter(User.id == i).first()
        user = _usr or User(id=i, name=f"name_{i}")
        _addrs = (
            sess.query(Address).filter(Address.id == i, Address.user == user).first()
        )
        addrs = _addrs or Address(id=i, street_address=f"{i} Foo St.", user=user)
        sess.add(user)
        sess.add(addrs)

        return

    session = Session(autoflush=False)
    threadmeister(total, save, sess=session)
    session.commit()
    session.close()

    return
