from asyncio import run
from pathlib import Path
from nextcord import AllowedMentions, Intents
from nextcord.ext.commands import Bot
from importlib import import_module
from typing import Union, Literal
from pyfigure import Configurable, Option

from src.cog import Cog, get_cogs
from src.databases import Database, get_db

class Principality(Bot, Configurable):

    config_file = 'configs/Bot.toml'

    def new_db(self, name: str) -> Database:
        return get_db(self.config.default_database_type, name)

    class Config:
        token: str = Option('', "Your bot's Discord token")
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