from sqlalchemy import text

from lib.commit_queue import SACommitQueue
from lib.db_functions import Engine
from lib.threadmeister import threadmeister


class SQEngineCommitQueue(SACommitQueue):
    """For using a SQLAlchemy Engine instead of a Session."""

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._db_thing = Engine

    def _commit(self):
        """Engine writer."""

        with self._locker:
            sqls = "".join(self._queue)
            with self._db_thing.begin() as conn:
                self._logger.debug(f"CONN: {id(conn)}")
                conn.execute(text(sqls))

        return


def main(total: int):
    """commits each record with a SQLAlchemy Engine-specific threaded commit queue using raw SQL;
    uses a PostgreSQL "upsert" to check if the item already exists"""

    def save(i, ecq):
        assert isinstance(i, int), f"{i} must be an int"
        stmnt = f"""
                INSERT INTO user_account (id, name)
                VALUES ({i}, 'name_{i}')
                ON CONFLICT (id)
                DO UPDATE SET name = 'name_{i}';
                
                INSERT INTO address (id, street_address, user_id)
                VALUES ({i}, '{i} Foo St.', {i})
                ON CONFLICT (id)
                DO UPDATE SET street_address = '{i} Foo St.', user_id = {i};"""

        ecq.load(stmnt)
        return

    sa_engine_commit_queue = SQEngineCommitQueue()
    threadmeister(total, save, ecq=sa_engine_commit_queue)
    sa_engine_commit_queue.save()

    return
