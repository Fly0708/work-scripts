import datetime
from typing import Annotated

import typer
import asyncssh
import asyncio
import os

app = typer.Typer()


class AsyncSSHClient:
    def __init__(
        self,
        host: str = None,
        username: str = None,
        port: int = 22,
        password: str = None,
    ):
        self.conn = None
        self.host = host
        self.username = username
        self.port = port
        self.password = password

    async def __aenter__(self):
        host = self.host
        username = self.username
        port = self.port
        password = self.password

        if not host:
            typer.secho("Error: SSH_HOST is required and cannot be empty.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        if not username:
            typer.secho("Error: SSH_USER is required and cannot be empty.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        if not password:
            typer.secho(
                "Error: SSH_PASSWORD is required and cannot be empty.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)

        try:
            self.conn = await asyncssh.connect(
                host,
                port=port,
                username=username,
                password=password,
                known_hosts=None,  # 相当于 paramiko 的 AutoAddPolicy
            )
            typer.secho("Connection successful.", fg=typer.colors.GREEN)
            return self.conn

        except asyncssh.PermissionDenied:
            typer.secho(
                "Authentication failed. Please check your credentials.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)
        except asyncssh.Error as e:
            typer.secho(f"SSH error occurred: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        except Exception as e:
            typer.secho(f"Connection error: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            typer.secho("Closing SSH connection.", fg=typer.colors.YELLOW)
            self.conn.close()

            # 等待连接关闭,设置超时避免卡住
            try:
                await asyncio.wait_for(self.conn.wait_closed(), timeout=2.0)
            except asyncio.TimeoutError:
                typer.secho("Warning: Connection close timeout", fg=typer.colors.YELLOW)

        return False


async def stream_log(host, port, username, password, log_base_path, log_file, log_level, number):
    process = None

    try:
        async with AsyncSSHClient(host, username, port, password) as conn:
            if log_base_path:
                target_log_file = (
                    f"{log_base_path}/{log_level}/{log_file}_{datetime.datetime.now().strftime('%Y-%m-%d')}.log"
                )
            else:
                target_log_file = f"{log_file}.log"

            command = f"tail -f -n {number} {target_log_file}"
            typer.secho(f"Executing command: {command}", fg=typer.colors.CYAN)

            process = await conn.create_process(command)

            try:
                async for line in process.stdout:
                    print(line.strip())

            except asyncio.CancelledError:
                typer.secho("\n--- Stopping log stream... ---", fg=typer.colors.YELLOW)
                raise

    except asyncio.CancelledError:
        if process and not process.is_closing():
            process.kill()

            try:
                await asyncio.wait_for(process.wait_closed(), timeout=1.0)
            except asyncio.TimeoutError:
                pass
        raise

    finally:
        if process and not process.is_closing():
            try:
                process.kill()
            except Exception:
                pass


@app.command()
def tail(
    ctx: typer.Context,
    log_file: Annotated[str, typer.Argument(..., help="日志文件名(不含 .log 后缀)")],
    log_level: Annotated[str, typer.Option()] = "debug",
    number: Annotated[int, typer.Option("-n")] = 50,
    host: Annotated[str, typer.Option(help="SSH 服务器地址")] = None,
    port: Annotated[int, typer.Option(help="SSH 服务器端口")] = 22,
    username: Annotated[str, typer.Option(help="SSH 用户名")] = None,
    password: Annotated[str, typer.Option(help="SSH 密码")] = None,
):
    try:
        asyncio.run(
            stream_log(
                host or ctx.obj.config.SSH_HOST,
                port or ctx.obj.config.SSH_PORT,
                username or ctx.obj.config.SSH_USER,
                password or ctx.obj.config.SSH_PASSWORD,
                ctx.obj.config.LOG_BASE_PATH,
                log_file,
                log_level,
                number,
            )
        )
    except KeyboardInterrupt:
        raise typer.Exit(code=0)
    except Exception as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
