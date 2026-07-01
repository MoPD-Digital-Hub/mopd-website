"""Load project .env before Django settings read os.environ."""

import os
from pathlib import Path


def load_env_file():
    base_dir = Path(__file__).resolve().parent.parent
    env_path = base_dir / '.env'
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()
