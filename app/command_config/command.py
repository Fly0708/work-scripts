from typing import Annotated

import typer

app = typer.Typer()


@app.command()
def init():
    """
    Initialize
    """
    from app.config import init_config

    from ..database import init_database

    init_config()
    typer.echo("Config initialized successfully.")

    try:
        init_database()
        typer.echo("Database initialized successfully.")
    except Exception as e:
        typer.echo(f"Warning: Failed to initialize database: {e}", err=True)


@app.callback(invoke_without_command=True)
def open_config(
    if_open_dir: Annotated[bool, typer.Option("--open-dir", "-d")] = True,
    if_edit: Annotated[bool, typer.Option("--edit-file", "-e")] = False,
):
    """
    Open the configuration file in the default editor.
    """
    from app.config import get_config_path

    from ..util.fs import open_folder_or_file

    config_path = get_config_path()
    if if_edit:
        open_folder_or_file(config_path)
    elif if_open_dir:
        open_folder_or_file(config_path.parent)


if __name__ == "__main__":
    app()
