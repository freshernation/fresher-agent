"""Settings for the agent.

Values come from the .env file next to this file. A real environment variable
with the same name wins over .env. To change a setting, edit .env, not this file.
"""

import os
from pathlib import Path

HERE = Path(__file__).parent

PROVIDERS = ("anthropic", "openai", "compatible", "fake")

DEFAULT_MODELS = {
    "anthropic": "claude-opus-5-5",
    "openai": "gpt-6-astra",
    "compatible": "",  # no sensible default: set MODEL in .env
    "fake": "fake",
}

KEY_NAMES = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "compatible": "COMPATIBLE_API_KEY",
}


def read_env_file(path):
    """Read KEY=value lines from a file into a dict. Missing file means no values."""
    values = {}
    if not path.exists():
        return values
    for line in path.read_text().splitlines():
        line = line.strip()
        if line == "" or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        values[name.strip()] = value.strip().strip('"').strip("'")
    return values


_FILE = read_env_file(HERE / ".env")


def get(name, default=""):
    return os.environ.get(name) or _FILE.get(name) or default


def api_key(provider):
    """The key for a provider, or "" if there is none."""
    return get(KEY_NAMES.get(provider, ""))


PROVIDER = get("PROVIDER", "anthropic").lower()
MODEL = get("MODEL") or DEFAULT_MODELS.get(PROVIDER, "")
MAX_STEPS = int(get("MAX_STEPS", "10"))
