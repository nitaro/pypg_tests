import sys
import traceback
from textwrap import indent


def easy_cli(locals_dict):
    """Makes all public functions runnable from a locals() dict."""

    funks = {
        k: v
        for k, v in locals_dict.items()
        if not k.startswith("_") and type(v).__name__ == "function" and v != easy_cli
    }

    if "-h" in sys.argv or len(sys.argv) == 1:
        br, tab = "\n", "\t"
        doc = "Available commands:\n"
        for k, v in funks.items():
            docstring = [ln.strip() for ln in v.__doc__.split("\n")]
            doc += f"{br} - {k}:{br} {indent(br.join(docstring).strip(), tab)}"
        doc += f"{br*2}Example:{br}{tab}$ python -m main describe"
        print(doc)
        return

    funk_to_run = funks.get(sys.argv[1])
    assert funk_to_run, f"No public function named: {sys.argv[1]}"

    try:
        result = funk_to_run()
        print(result or "OK")
        sys.exit()
    except Exception as err:
        traceback.print_exception(err)
        sys.exit(1)
