import asyncio

import typer

from app.internal.models.user import create_super_user

name = input('Enter you name: ')
password = input('Enter you password: ')
asyncio.run(create_super_user(name, password))
print("Done")
