from . import Cherub
from typer import Typer, run
from typing import List

cherub = Cherub()
app = Typer()

@app.command()
def update(cog: str):
    pass

@app.command()
def check(cog: str):
    pass

@app.command()
def delete(cog: str, delete_data: bool = True, delete_config: bool = False):
    cherub.delete(cog, delete_data, delete_config)

@app.command_group()
def list():
    pass

@list.command()
def installed():
    print('Installed Modules:')
    print('\n'.join(cherub.installed_cogs()))

@list.command()
def available():
    cherub.list_available()

@app.command()
def install(cogs: List[str]):
    pass

if __name__ == '__main__':
    app()
    print('e')