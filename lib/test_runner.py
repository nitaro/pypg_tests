# No public functions take any arguments - that makes it easy to have a simple CLI interface.
# It also makes things simpler overall.

import logging
import os
import subprocess
from csv import DictWriter
from datetime import datetime
from pathlib import Path
from time import perf_counter

import memray
from memray._memray import compute_statistics

from lib.config import CONFIG, ENV_TEXT

from .db_functions import count_rows as _count_rows
from .db_functions import drop_rows as _drop_rows


def _funk_map():
    """Returns a dict of all test module names (keys) and their main() functions (values)."""

    test_path = Path(__file__).parent.parent.joinpath("db_tests")
    stems = sorted(
        [p.stem for p in test_path.glob("*.py") if not p.stem.startswith("_")]
    )
    mod = __import__(test_path.stem, fromlist=stems)

    return {stem: getattr(mod, stem).main for stem in stems}


def describe():
    """Prints Markdown string of test file names and their descriptions."""

    fmap = _funk_map()

    md = ["# Test Descriptions", "\n"]
    for i, k in enumerate(fmap):
        test = f"{i + 1}. `{k}()`"
        description = f"\t- {fmap[k].__doc__}"
        md.extend([test, description])

    return "\n".join(md)


def test_one():
    """Runs a User-selected test from a dropdown list.

    Example:
        python -m main drop_rows
        python -m main test_one  # insert
        python -m main test_one  # update"""

    log_path = Path(__file__).parent.parent.joinpath("_.log")
    log_path.unlink(True)

    fh = logging.FileHandler(log_path)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(thread)d - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    logging.root.setLevel(logging.DEBUG)
    logging.root.propagate = True
    logging.root.addHandler(fh)

    choices = {}
    for i, kv in enumerate(_funk_map().items()):
        choices[i] = kv

    lines = ["Choose a test's number to run it:\n"]
    lines.extend([f"{i}) {kv[0]}" for i, kv in choices.items()])
    print("\n".join(lines))

    selection = input("")
    assert selection.isdigit(), "You must enter a number."
    selection = int(selection)
    assert selection in choices, "Invalid choice."

    test_name, test_func = choices[selection]
    logging.info(f"Running test_one for: {test_name}")
    test_func(int(CONFIG.TOTAL_ITEMS))

    return


def test_all():
    """Runs all tests and creates data files in /results."""

    test_run_dir = Path(__file__).parent.parent.joinpath("results/")
    test_run_dir.mkdir(parents=True, exist_ok=True)

    test_run_id = datetime.now().strftime("%Y%m%d_%I%M%S_%p%f")
    csv_file = test_run_dir.joinpath(f"{test_run_id}.csv")
    csv_io = csv_file.open("w")

    fh = logging.FileHandler(Path(str(csv_file).replace(".csv", ".log")))
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(thread)d - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    logging.root.setLevel(logging.DEBUG)
    logging.root.propagate = True
    logging.root.addHandler(fh)

    # write csv file.
    writer = DictWriter(
        csv_io,
        fieldnames=["test", "totals", "success", "duration", "memory"],
    )
    writer.writeheader()
    csv_io.flush()

    for name, funk in _funk_map().items():
        for write_type in ["insert", "update"]:
            logging.info("dropping everything ...")
            logging.info(f"Running {name} with {write_type.upper()}.")
            _drop_rows()

            start = perf_counter()

            bin_file = test_run_dir.joinpath("_.bin")
            with memray.Tracker(bin_file):
                funk(int(CONFIG.TOTAL_ITEMS))

            run_time = perf_counter() - start

            # per: https://github.com/bloomberg/memray/blob/main/src/memray/commands/stats.py#L62
            memory_used = compute_statistics(os.fspath(bin_file)).total_memory_allocated
            bin_file.unlink()

            row_counts = _count_rows()
            writer.writerow(
                {
                    "test": name + "-" + write_type,
                    # "description": funk.__doc__,
                    "totals": row_counts,
                    "success": row_counts[0]
                    == row_counts[1]
                    == int(CONFIG.TOTAL_ITEMS),
                    "duration": run_time,
                    "memory": memory_used / 1024 / 1024,  # megabytes.
                }
            )

            csv_io.flush()

    csv_io.close()

    # make git diff file.
    cmd = subprocess.run("git log -1; echo; git diff", shell=True, capture_output=True)
    gitfile = Path(str(csv_file).replace(".csv", ".diff"))
    gitfile.write_bytes(cmd.stdout)

    # make config file.
    config_file = Path(str(csv_file).replace(".csv", ".conf"))
    config_file.write_text(ENV_TEXT)

    return test_run_id
