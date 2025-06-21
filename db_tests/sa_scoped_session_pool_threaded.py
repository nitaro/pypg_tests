import logging
from threading import Lock, get_ident

from lib.db_functions import ScopedSession
from lib.models import Address, User
from lib.threadmeister import threadmeister


class SASessionPooler:
    """Trying to use a ScopedSession per thread."""

    def __init__(self):
        self._pool = {}
        self._locker = Lock

    def get(self):
        with self._locker():
            thread_id = get_ident()
            logging.info(f"thread id: {thread_id}")

            if thread_id not in self._pool:
                pool_sess = ScopedSession()
                self._pool[thread_id] = pool_sess
            else:
                pool_sess = self._pool[thread_id]

        return pool_sess

    def save(self):
        with self._locker():
            try:
                for pool_q in self._pool.values():
                    pool_q.commit()
            except Exception as err:
                self._logger.error(err)

        return


def main(total: int):
    """commits each record with threaded pool of SQLAlchemy scoped sessions using raw SQL;
    uses the ORM to first check if the items exist in the db"""

    def save(i, sess_pool):
        sess = sess_pool.get()

        _usr = sess.query(User).filter(User.id == i).first()
        user = _usr or User(id=i, name=f"name_{i}")
        _addrs = (
            sess.query(Address).filter(Address.id == i, Address.user == user).first()
        )
        addrs = _addrs or Address(id=i, street_address=f"{i} Foo St.", user=user)
        sess.add(user)
        sess.add(addrs)
        sess.commit()

        return

    sa_session_pool = SASessionPooler()
    threadmeister(total, save, sess_pool=sa_session_pool)
    sa_session_pool.save()

    return
