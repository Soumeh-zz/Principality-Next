from . import Cherub
from typer import Typer
from typing import List, Union

cherub = Cherub()
app = Typer(pretty_exceptions_show_locals=False, pretty_exceptions_short=True)

@app.command()
def new():

    name = None
    print("What should your cog be named?")
    while not name: name = input("Name: ")

    id = None
    print("What should be the identifier of your cog?")
    while not id: id = input("ID: ")

    author = None
    print("How should you be credited?")
    while not author: author = input("Author: ")
    author = '[{ name = "' + author + '" }]'

    print("What does the cog do?")
    description = input("Description: ")
    
    pyproject = f'''[project]
name = "{name}"
description = "{description}"
version = "1.0"
authors = {author}
'''

    code = f'''from cog import Cog, ConfigOption, SlashOption

class {name.replace(' ', '')}(Cog):

    # Built-in attributes:
    # self.directory - Returns the Path object of the folder containing this cog

    class Config:
        is_true: bool = ConfigOption(True, "Whether or not this value is true")

    def load(self, bot):
        # runs when the bot initializes cogs
        print('Loaded!')

    async def ready(self, bot):
        # runs when the bot is fully loaded
        print('Async Loaded!')

    @Cog.slash_command()
    async def test(self, ctx):
        await ctx.response.send_message("This value is " + str(self.config['is_true']) )

    @Cog.listener()
    async def on_member_join(self, member):
        print(member)
'''
    
    cog_dir = cherub.cog_directory / id
    cog_dir.mkdir()
    pyproject_file = cog_dir / 'pyproject.toml'
    pyproject_file.write_text(pyproject)
    code_file = cog_dir / 'src' / f'{id}.py'
    code_file.parent.mkdir()
    code_file.write_text(code)
    print('\nSuccessfully created a new cog!')

@app.command()
def install(cogs: List[str]):
    for cog in cogs:
        done = cherub.install(cog)
        if done: print(f"Installed cog '{cog}'")

@app.command()
def update(cogs: List[str]):
    if cogs[0].lower() == 'all':
        for cog in cherub.cogs.keys():
            cherub.update(cog)
            print(f"Updated cog '{cog}'")
    else:
        for cog in cogs:
            cherub.update(cog)
            print(f"Updated cog '{cog}'")

@app.command()
def delete(cogs: List[str], delete_data: bool = True, delete_config: bool = False):
    for cog in cogs:
        cherub.delete(cog, delete_data, delete_config)
        print(f"Deleted cog '{cog}'")

@app.command()
def populate():
    cherub.populate()
    print(f"Populated cogs")

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

def main():
    app()

if __name__ == '__main__':
    main()
