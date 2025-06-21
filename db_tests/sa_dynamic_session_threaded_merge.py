from lib.db_functions import Session
from lib.models import Address, User
from lib.threadmeister import threadmeister


def main(total: int):
    """commits each record with a new SQLAlchemy Session per commit, using threads;
    uses the ORM's "merge" method"""

    def save(i):
        with Session() as sess:
            user = User(id=i, name=f"name_{i}")
            address = Address(id=i, street_address=f"{i} Foo St.", user=user)
            sess.merge(user)
            sess.merge(address)
            sess.commit()

        return

    threadmeister(total, save)

    return
