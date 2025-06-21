import logging
from collections import deque
from contextlib import nullcontext
from threading import RLock

from sqlalchemy import text

from .db_functions import ScopedSession


class SACommitQueue:
    """Commits SQLAlchemy ORM objects to the database when @max_size objects are submitted to the load() method.
    After the commit, the queue is cleared. Upon exit, leftover items objects in the queue are committed.

    Set @thread_safe to False to disable the thread lock. This is not recommended."""

    def __init__(self, max_size=250, thread_safe=True):
        assert isinstance(max_size, int), "max_size must be an int"
        assert max_size >= 0, "max_size must be >= 0"

        self.max_size = max_size
        self._queue = deque(maxlen=self.max_size)
        self._locker = RLock() if thread_safe else nullcontext()
        self._db_thing = ScopedSession
        self._logger = logging.getLogger(self.__class__.__name__)

    def _commit(self):
        """Write to the database using @self._db_thing. Override as needed."""

        with self._locker:
            sqls = "".join(self._queue)
            with self._db_thing() as sess:
                sess.execute(text(sqls))
                sess.commit()

        return

    def save(self):
        """Commits everything to the database."""

        self._logger.info("Committing statements to database.")

        with self._locker:
            try:
                self._commit()
                self._queue.clear()
            except Exception as err:
                self._logger.error(err)

        return

    def load(self, sql):
        """Adds a @sql to the queu of objects to commit.
        If the queue is full, runs @self._save and clears the queue.
        A @sql can be anything. What matters is that @self._commit know how to handle a
        deque of them."""

        with self._locker:
            self._logger.debug(f"Adding statement: {sql}")
            self._queue.append(sql)
            if len(self._queue) == self.max_size:
                self._logger.info(f"Queue limit of {self.max_size} reached.")
                self.save()

        return
