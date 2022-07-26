from . import Cherub
from typer import Typer
from typing import List, Union

cherub = Cherub()
app = Typer(pretty_exceptions_show_locals=False, pretty_exceptions_short=True)

@app.command()
def install(cogs: List[str]):
    for cog in cogs:
        cherub.install(cog)

@app.command()
def update(cogs: List[str]):
    if cogs[0].lower() == 'all':
        for cog in cherub.db['cogs'].keys():
            cherub.update(cog)
    else:
        for cog in cogs:
            cherub.update(cog)

@app.command()
def remove(cogs: List[str], delete_data: bool = True, delete_config: bool = False):
    for cog in cogs:
        cherub.delete(cog, delete_data, delete_config)

@app.command()
def populate():
    cherub.populate()

@app.command_group()
def list():
    pass

@list.command()
def installed():
    #cherub.populate()
    cogs = [c['name'] for c in cherub.cogs.values()]
    print('Installed Cogs:')
    print('\n'.join(cogs))

@list.command()
def available():
    cherub._cog_exists('')
    print('Available Cogs:')
    available = [a for a in cherub.available_cogs if a not in cherub.cogs]
    print('\n'.join(available) or "None :(")

if __name__ == '__main__':
    app()
    print('e')