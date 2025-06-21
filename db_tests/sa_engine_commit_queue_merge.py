from lib.threadmeister import threadmeister

from .sa_engine_commit_queue_upsert import SQEngineCommitQueue


# helpful re: use of USING: https://stackoverflow.com/a/17267423
def main(total: int):
    """commits each record with a SQLAlchemy Engine-specific threaded commit queue using raw SQL;
    uses a PostgreSQL "MERGE" to check if the item already exists"""

    def save(i, ecq):
        assert isinstance(i, int), f"{i} must be an int"
        stmnt = f"""
                MERGE INTO user_account
                USING (VALUES ({i})) AS vals (id)
                ON vals.id = user_account.id
                WHEN NOT MATCHED THEN
                    INSERT (id, name)
                    VALUES({i}, 'name_{i}')
                WHEN MATCHED THEN
                    UPDATE SET
                        name = 'name_{i}';

                MERGE INTO address
                USING (VALUES ({i})) AS vals (id)
                ON vals.id = address.id
                WHEN NOT MATCHED THEN
                    INSERT (id, street_address, user_id)
                    VALUES ({i}, '{i} Foo St.', {i})
                WHEN MATCHED THEN
                    UPDATE SET
                        street_address = '{i} Foo St.', user_id = {i};"""

        ecq.load(stmnt)
        return

    sa_engine_commit_queue = SQEngineCommitQueue()
    threadmeister(total, save, ecq=sa_engine_commit_queue)

    sa_engine_commit_queue.save()

    return
