from asyncio import run
from pathlib import Path
from nextcord import AllowedMentions, Intents
from nextcord.ext.commands import Bot
from typing import Literal
from pyfigure import Configurable, Option
from nextcord.ext import tasks

from principality.cog import Cog, get_cogs
from principality.databases import Database, get_db
from principality.overseer import Overseer

class Principality(Bot, Configurable):

    config_file = 'configs/Bot.toml'

    def new_db(self, name: str) -> Database:
        return get_db(self.config.default_database_type, name)

    class Config:
        token_env_vear: str = Option('TOKEN', "The environmental variable of your bot's token. (Leave as default unless you want to work with multiple bots)")
        cog_folder: str = Option('cogs', "What directory to load modules from")
        cog_databases: bool = Option(True, "Whether or not every cog should generate a database for itself (accessible using `self.db`)")
        default_database_type: Literal['local', 'temp', 'deta'] = Option('local', "What database type to use for cogs (Options: local, temp or deta)")

    def __init__(self):
        Bot.__init__(self, intents=Intents.all(), allowed_mentions=AllowedMentions(everyone=False, replied_user=False))
        Configurable.__init__(self)

        run(self.__async__())
    
    async def __async__(self):
        cogs = get_cogs(Path(self.config.cog_folder))
        for cog in cogs:
            cog = cog()
            if self.config.cog_databases:
                cog.db = self.new_db(cog.name)
            await self.load_cog(cog)
        print('Loaded Modules: \n' + '\n'.join(self.cogs.keys()))

    async def on_ready(self):
        for name, cog in self.cogs.items():
            try:
                await self.async_load_cog(cog)
            except Exception as error:
                exception_type = type(error).__name__
                exception_message = error
                exception_line = error.__traceback__.tb_lineno
                print(f"Error in cog '{name}' on line {exception_line}: [{exception_type}] {exception_message}")

    async def load_cog(self, cog: Cog):
        cog.bot = self
        self.add_cog(cog, override=True)
        if hasattr(cog, 'load'): cog.load()

    async def async_load_cog(self, cog: Cog):
        if hasattr(cog, 'ready'): await cog.ready()

    async def unload_cog(self, cog: Cog):
        self.remove_cog(cog.__cog_name__)



class PrincipalityDev(Principality):

    async def on_ready(self):
        await super().on_ready()
        self.config_overseer = Overseer(self.config_folder, '*.toml')
        self.cog_overseer = Overseer(Path(self.config['cog_folder']), ['**/*.py', '**/*.json'])
        await self.update_checker.start()



    @tasks.loop(seconds=5)
    async def update_checker(self):

        # check configs
        changed, added, removed = self.config_overseer.changes()

        for file in changed.union(removed):
            file_name = file.stem
            cog_folder = Path(self.config['cog_folder']) / file_name
            module = import_module(Path(self.config['cog_folder']).stem+'.'+file_name)
            for temp_cog in self.cogs_from_module(module):
                cog_name = temp_cog().__cog_name__
                cog = self.cogs[cog_name]
                cog.reload_config()
                print(f"Reloaded config for cog '{cog_name}'")

        # check cogs
        changed, added, removed = self.cog_overseer.changes()
        functions = {'changed': changed, 'added': added, 'removed': removed}

        for function, list in functions.items():
            for file in list:
                file_name = file.parent.stem
                cog_folder = Path(self.config['cog_folder']) / file_name

                module = import_module(Path(self.config['cog_folder']).stem+'.'+file_name)
                if function == 'changed':
                    reload(module)

                for cog in self.cogs_from_module(module):
                    cog = cog()
                    if function != 'removed':
                        await self.load_cog(cog, cog_folder)
                        await self.async_load_cog(cog)
                    else:
                        await self.unload_cog(cog)