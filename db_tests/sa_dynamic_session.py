from lib.db_functions import Session
from lib.models import Address, User


def main(total: int):
    """commits each record with a new SQLAlchemy Session per commit;
    uses the ORM to first check if the items exist in the db"""

    for i in range(total):
        with Session(autoflush=False) as sess:
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

    return
