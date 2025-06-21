import os
from pathlib import Path

env_file = Path(__file__).parent.parent.joinpath(".env")
ENV_TEXT = env_file.read_text()
conf = {}
for line in ENV_TEXT.splitlines():
    env_var = line.partition("=")[0].replace("export", "").strip()
    conf[env_var] = os.environ.get(env_var)


CONFIG = type("CONFIG", tuple(), conf)
