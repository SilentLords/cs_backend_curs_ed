import asyncio

import typer

from app.pkg.postgresql import init_models

import typer

app = typer.Typer()

#
# @app.command()
# def hello(name: str):
#     print(f"Hello {name}")
#
#
# @app.command()
# def goodbye(name: str, formal: bool = False):
#     if formal:
#         print(f"Goodbye Ms. {name}. Have a good day.")
#     else:
#         print(f"Bye {name}!")
@app.command()
def db_init_models():
    asyncio.run(init_models())
    print("Done")


if __name__ == "__main__":
    app()

# cli = typer.Typer()
#
#
# @cli.command()
# def db_init_models():
#     asyncio.run(init_models())
#     print("Done")
#
#
# if __name__ == "__main__":
#     cli()