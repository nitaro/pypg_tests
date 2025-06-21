# flake8: noqa

from lib.easy_cli import easy_cli  # isort:skip

from lib.db_functions import *  # isort:skip
from lib.test_runner import *  # isort:skip

from lib.grapher import *  # isort:skip


if __name__ == "__main__":
    from lib.easy_cli import easy_cli

    easy_cli(locals())
