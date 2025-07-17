import click

from .webserver import create_app


@click.command(help="Run the spotify actions web server")
@click.option("--host", default="127.0.0.1", help="Host address")
@click.option("--port", default=5000, type=int, help="Port number")
def run(host: str, port: int) -> None:
    app = create_app()
    app.run(host=host, port=port)


if __name__ == "__main__":  # pragma: no cover
    run()
