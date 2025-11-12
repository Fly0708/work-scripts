import typer

from app.context_schema import ContextSchema

app = typer.Typer()

from .command_config.command import app as config_app

app.add_typer(config_app, name="config", help="配置相关命令")

from .command_ssh.command import app as ssh_app

app.add_typer(ssh_app, name="ssh-log", help="SSH相关命令")


@app.callback()
def callback(ctx: typer.Context):
    from app.config import init_config, read_config

    init_config()

    ctx.ensure_object(ContextSchema)
    ctx.obj.config = read_config()


if __name__ == "__main__":
    app()
