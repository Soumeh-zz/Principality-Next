from . import Cherub
from typer import Typer
from typing import List, Union

cherub = Cherub()
app = Typer()

@app.command()
def install(cogs: List[str]):
    for cog in cogs:
        cherub.install(cog)
    cherub.save_requirements()

@app.command()
def update(cogs: List[str]):
    if cogs[0].lower() == 'all':
        for cog in cherub.db['cogs'].keys():
            cherub.update(cog)
    else:
        for cog in cogs:
            cherub.update(cog)
    cherub.save_requirements()

@app.command()
def delete(cog: str, delete_data: bool = True, delete_config: bool = False):
    cherub.delete(cog, delete_data, delete_config)

@app.command()
def populate():
    cherub.populate()

@app.command_group()
def list():
    pass

@list.command()
def installed():
    print('Installed Modules:')
    print('\n'.join(cherub.installed_cogs()))

@list.command()
def available():
    cherub._cog_exists()
    print('Available Modules:')
    print('\n'.join(cherub.cherub.available))

if __name__ == '__main__':
    app()
    print('e')