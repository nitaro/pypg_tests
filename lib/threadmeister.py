import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import CONFIG


def threadmeister(total, func, number_of_threads=int(CONFIG.TOTAL_THREADS), **kw):
    """Runs @func for a @total number of times using a given @number_of_threads."""

    logging.info(f"Thread count: {number_of_threads}")

    futures = []
    with ThreadPoolExecutor(max_workers=number_of_threads) as executor:
        for i in range(total):
            futures.append(executor.submit(func, i, **kw))
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                logging.error("generated an exception: %s" % (exc))

    return
