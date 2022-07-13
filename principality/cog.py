from pathlib import Path

import nextcord
from nextcord.ext.commands import Cog as DiscordCog
from tomlkit import load, table
from pyfigure import Configurable, Option

# Util Functions

async def reply(ctx, message):
    await ctx.response.send_message(embed=nextcord.Embed(description=message))

# Classes

class ConfigOption(Option):
    pass

class SlashOption(nextcord.SlashOption):
    pass

class Cog(DiscordCog, Configurable):

    config_directory = Path('configs')
    slash_command = nextcord.slash_command
    user_command = nextcord.user_command
    message_command = nextcord.message_command
    command = nextcord.ext.commands.command

    def __init__(self):

        self.name = self.__class__.__name__
        self.config_file = self.config_directory / (self.name+'.toml')

        Configurable.__init__(self)

        # read metadata
        toml_file = self.directory.parent / 'pyproject.toml'
        if toml_file.exists() and toml_file.is_file():
            with open(toml_file, 'r') as file:
                toml = load(file)
        else:
            toml = table()
        self.metadata = table()
        for _, data in toml.items():
            for key, value in data.items():
                self.metadata[key] = value
                setattr(self.metadata, key, value)

from importlib.util import spec_from_file_location, module_from_spec
from inspect import isclass, getmembers
from typing import List

def get_cogs(path: Path) -> List[Cog]:
    cogs = []
    for dir in _cog_dirs_from_dir(path):
        dir = dir.parent
        module = _cog_modules_from_dir(dir)
        for cog in _cogs_from_module(module, dir):
            cogs.append(cog)
    return cogs

def _cog_dirs_from_dir(path: Path):
    return path.rglob('*/pyproject.toml')

def _cog_modules_from_dir(path: Path):
    spec = spec_from_file_location(path.stem, path/'src'/(str(path.stem)+'.py'))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def _cogs_from_module(module, path: Path):
    for cog in [c[1] for c in getmembers(module, isclass)]:
        if issubclass(cog, Cog) and cog != Cog:
            cog.directory = path/'src/'
            yield cog