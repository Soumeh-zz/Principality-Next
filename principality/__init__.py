from asyncio import run
from pathlib import Path
from nextcord import AllowedMentions, Intents
from nextcord.ext.commands import Bot
from typing import Literal
from pyfigure import Configurable, Option
from nextcord.ext import tasks

from cog import Cog, get_cogs
from principality.overseer import Overseer

class Principality(Bot, Configurable):

    config_directory = Path('configs/')
    config_file = config_directory/'Bot.toml'

    class Config:
        cog_directory: str = Option('cogs', "What directory to load modules from")

        token_env_var: str = Option('TOKEN', "The environmental variable of your bot's token. (Leave as default unless you want to work with multiple bots)")
        cog_databases: bool = Option(True, "Whether or not every cog should generate a database for itself (accessible using `self.db`)")
        default_database_type: Literal['local', 'temp', 'deta'] = Option('local', "What database type to use for cogs (Options: local, temp or deta)")

    def __init__(self, *args):

        Bot.__init__(self, rollout_all_guilds=True, intents=Intents.all(), allowed_mentions=AllowedMentions(everyone=False, replied_user=False), *args)
        Configurable.__init__(self)

    def load(self):
        print('Loaded Cogs:')
        cogs = get_cogs(Path(self.config.cog_directory))
        for cog in cogs.values():
            db = None
            if self.config.cog_databases: db = self.config.default_database_type
            cog = cog(db)
            self.add_cog(cog)
            self.load_cog(cog)
            print('> '+cog.name)

    async def on_ready(self):
        for cog in self.cogs.values():
            await self.async_load_cog(cog)

    def add_cog(self, cog: Cog):
        cog.bot = self
        super().add_cog(cog, override=True)
        return True

    def load_cog(self, cog: Cog):
        try:
            if hasattr(cog, 'load'): cog.load()
            return True
        except Exception as error:
            exception_type = type(error).__name__
            exception_message = error
            exception_line = error.__traceback__.tb_lineno
            print(f"Error while loading cog '{cog.name}' on line {exception_line}: [{exception_type}] {exception_message}")

    async def async_load_cog(self, cog: Cog):
        try:
            if hasattr(cog, 'ready'): await cog.ready()
            return True
        except Exception as error:
            exception_type = type(error).__name__
            exception_message = error
            exception_line = error.__traceback__.tb_lineno
            print(f"Error while readying cog '{cog.name}' on line {exception_line}: [{exception_type}] {exception_message}")

    async def unload_cog(self, cog: Cog):
        self.remove_cog(cog.id)
        return True
    
    async def reload_cog(self, cog: Cog):
        await self.unload_cog(cog)
        # reload module
        self.load_cog(cog)
        await self.async_load_cog(cog)
        return True



class PrincipalityDev(Principality):

    found_cogs = {}

    async def on_ready(self):
        await super().on_ready()
        self.config_overseer = Overseer(self.config_directory, '*.toml')
        self.cog_overseer = Overseer(Path(self.config.cog_directory), ['*.py', '*.toml', '*.json'])
        await self.update_checker.start()

    @tasks.loop(seconds=5)
    async def update_checker(self):

        # check configs
        changed, _, _ = self.config_overseer.changes()
        for file in changed:
            cog_id = file.stem
            cog = self.cogs.get(cog_id, None)
            if not cog:
                print("Non-Cog configuration file edited, you'll have to restart your bot manually to apply changes")
                continue
            cog.reload_config()
            print(f"Reloaded config for cog '{cog_id}'")

        # check cogs
        self.processed_cogs = []
        changed, added, removed = self.cog_overseer.changes()

        for file in removed:
            if file.name != 'pyproject.toml':
                continue
            cog = self.cogs[file.parent.stem]
            await self.unload_cog(cog)
            await self.sync_application_commands()
            print(f"Removed cog '{cog.name}'")
            removed = {r for r in removed if not r.is_relative_to(file.parent)}

        for file in added:
            if file.name != 'pyproject.toml':
                continue
            cog = Cog.from_dir(file.parent)
            cog = cog()
            cog.bot = self
            self.add_cog(cog)
            self.load_cog(cog)
            await self.async_load_cog(cog)
            await self.sync_application_commands()
            print(f"Added cog '{cog.name}'")
            added = {a for a in added if not a.is_relative_to(file.parent)}

        files = changed.union(added).union(removed)
        for file in files:
            # find cog id and cache it
            cog_dir = await self.find_cog(file)
            if not cog_dir:
                print(f"Couldn't find what cog file '{file}' belongs to")
                continue

            cog = Cog.from_dir(cog_dir)

            if cog in self.processed_cogs:
                continue

            cog = cog()
            self.load_cog(cog)
            await self.async_load_cog(cog)
            await self.sync_application_commands()

            self.processed_cogs.append(cog)
            print(f"Reloaded cog '{cog.name}'")

    async def find_cog(self, path: Path) -> str:
        cog_dir = self.found_cogs.get(path, None)
        if not cog_dir:
            if path.name == 'pyproject.toml':
                cog_dir = path.parent
            else:
                cog_dir = self._find_cog(path)
                if not cog_dir:
                    return None

        self.found_cogs[path] = cog_dir
        return cog_dir

    def _find_cog(self, path: Path) -> str:
        if path == Path('.'):
            return None
        files = [i for i in path.glob('pyproject.toml')]
        if len(files) < 1:
            return self._find_cog(path.parent)
        if len(files) > 1:
            return None
        return files[0].parent