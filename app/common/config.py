import os
from pathlib import Path

from pydantic import BaseModel


class ConfigSchema(BaseModel):
    SSH_HOST: str
    SSH_USER: str
    SSH_PORT: int = 22
    SSH_PASSWORD: str
    LOG_BASE_PATH: str


def get_config_path():
    if os.name == "nt":
        config_dir = Path(os.getenv("APPDATA")) / "work_scripts"
    else:
        config_dir = Path.home() / ".config" / "work_scripts"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def init_config():
    config_path = get_config_path()
    if not config_path.exists():
        default_config = ConfigSchema(
            SSH_HOST="", SSH_PORT=22, SSH_USER="", SSH_PASSWORD="", LOG_BASE_PATH=""
        ).model_dump()

        with open(config_path, "w") as f:
            import json

            json.dump(default_config, f, indent=4)


def read_config() -> ConfigSchema:
    config_path = get_config_path()
    with open(config_path, "r") as f:
        import json

        payload = json.load(f)

    return ConfigSchema.model_validate(payload)
