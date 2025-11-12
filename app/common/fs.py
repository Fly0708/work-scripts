import os
import random
import string
from pathlib import Path


def get_random_string(length=8):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def open_folder_or_file(path: str | Path):
    if isinstance(path, Path):
        path = str(path)
    if os.name == "nt":  # Windows
        os.startfile(path)
    elif os.name == "posix":
        import sys
        import subprocess

        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", path], check=False)
        else:  # Linux and other POSIX
            subprocess.run(["xdg-open", path], check=False)
    else:
        raise NotImplementedError(f"open_folder is not implemented for OS: {os.name}")
