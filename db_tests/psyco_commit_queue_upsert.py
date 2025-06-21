import psycopg2

from lib.commit_queue import SACommitQueue
from lib.config import CONFIG
from lib.threadmeister import threadmeister


class PsycoCommitQueue(SACommitQueue):
    """For bypassing the ORM and using Psycopg directly."""

    def __init__(
        self,
        connection_string=f"dbname={CONFIG.DB_NAME} user={CONFIG.DB_USER} password={CONFIG.DB_PASSWORD}",
        *args,
        **kwargs,
    ):
        assert isinstance(connection_string, str), "Connection string must be a string"
        super().__init__(*args, **kwargs)
        self._db_thing = psycopg2.connect(connection_string)  # connection.

    def _commit(self):
        """Psycopg writer."""

        with self._locker:
            sqls = "".join(self._queue)
            cur = self._db_thing.cursor()
            cur.execute(sqls)
            self._db_thing.commit()
            cur.close()

        return

    def close(self):
        return self._db_thing.close()


def main(total: int):
    """commits each record with a Pyscopg-specific threaded commit queue using raw SQL;
    uses a PostgreSQL "upsert" to check if the item already exists"""

    def save(i, pcq):
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

        pcq.load(stmnt)
        return

    psyco_commit_queue = PsycoCommitQueue()
    threadmeister(total, save, pcq=psyco_commit_queue)

    psyco_commit_queue.save()
    psyco_commit_queue.close()

    return
