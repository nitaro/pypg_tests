from lib.db_functions import Session
from lib.models import Address, User


def main(total: int):
    """commits each record with a static SQLAlchemy Session;
    uses the ORM's "merge" method"""

    sess = Session(autoflush=False)
    for i in range(total):
        user = User(id=i, name=f"name_{i}")
        sess.merge(user)

        sess.commit()
        """without a commit here I get:
        sqlalchemy.exc.IntegrityError: (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "user_account_pkey"
        DETAIL:  Key (id)=(0) already exists." IF the User does not already exist (i.e. was dropped in advance).
        
        I'm probably doing something wrong, but this is exactly the point - I'm futzing around with the ORM instead of getting work done.
        Just read all the merge caveats here: https://docs.sqlalchemy.org/en/20/orm/session_state_management.html#merge-tips
        and ask yourself if this is what you want to deal with?
        """

        address = Address(id=i, street_address=f"{i} Foo St.", user=user)
        sess.merge(address)

    sess.commit()
    sess.close()

    return
