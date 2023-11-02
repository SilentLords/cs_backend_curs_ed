import asyncio

import typer

from app.pkg.postgresql import init_models

cli = typer.Typer()


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    print("Done")
