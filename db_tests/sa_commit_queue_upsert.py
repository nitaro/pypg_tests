from lib.commit_queue import SACommitQueue
from lib.threadmeister import threadmeister


def main(total: int):
    """commits each record with a SQLAlchemy session-specific threaded commit queue using raw SQL;
    uses a PostgreSQL "upsert" to check if the item already exists"""

    def save(i, sacq):
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

        sacq.load(stmnt)
        return

    sa_commit_queue = SACommitQueue()
    threadmeister(total, save, sacq=sa_commit_queue)
    sa_commit_queue.save()

    return
