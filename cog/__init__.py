from pathlib import Path
from superdict import SuperDict

import nextcord
from nextcord.ext.commands import Cog as DiscordCog
from tomlkit import load
from pyfigure import Configurable, Option
from importlib.util import spec_from_file_location, module_from_spec
from inspect import isclass, getmembers
from typing import List

from principality.databases import Database, get_db

class ConfigOption(Option):
    pass

class SlashOption(nextcord.SlashOption):
    pass

class Cog(DiscordCog, Configurable):

    config_directory = Path('configs/')

    slash_command = nextcord.slash_command
    user_command = nextcord.user_command
    message_command = nextcord.message_command
    command = nextcord.ext.commands.command

    @classmethod
    def from_dir(self, path: Path):
        spec = spec_from_file_location(path.stem, path/'src'/(str(path.stem)+'.py'))
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        cog = _cogs_from_module(module)[0]
        cog.directory = path/'src/'
        return cog

    def __init__(self, database: Database = None):

        # read metadata
        project_file = self.directory.parent / 'pyproject.toml'
        with open(project_file, 'r') as file:
            self.metadata = SuperDict(load(file)['project'])

        # setup data
        self.name = self.metadata.name
        self.id = self.directory.parent.stem
        self.__cog_name__ = self.id
        self.config_file = self.config_directory / (self.id+'.toml')

        Configurable.__init__(self)

        # gen database
        if database:
            self.db = get_db(database, self.name)


def get_cogs(path: Path) -> List[Cog]:
    cogs = {}
    for dir in path.rglob('*/pyproject.toml'):
        cog = Cog.from_dir(dir.parent)
        cogs[dir.parent.stem] = cog
    return cogs

def _cogs_from_module(module):
    cogs = []
    for cog in [c[1] for c in getmembers(module, isclass)]:
        if issubclass(cog, Cog) and cog != Cog:
            cogs.append(cog)
    return cogs