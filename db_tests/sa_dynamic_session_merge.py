from lib.db_functions import Session
from lib.models import Address, User


def main(total: int):
    """commits each record with a new SQLAlchemy Session per commit;
    uses the ORM's "merge" method"""

    for i in range(total):
        with Session(autoflush=False) as sess:
            user = User(id=i, name=f"name_{i}")
            address = Address(id=i, street_address=f"{i} Foo St.", user=user)
            sess.merge(user)
            sess.commit()
            sess.merge(address)
            sess.commit()
            sess.close()

    return
