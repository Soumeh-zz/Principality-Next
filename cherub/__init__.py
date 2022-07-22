from importlib import import_module
from inspect import getmembers, isclass
from json import loads
from pathlib import Path
from shutil import copyfileobj
from sys import argv, modules
from urllib.error import HTTPError
import urllib.request

from typing import List

from pyfigure import Configurable, Option
from principality.databases import Local
from principality.cog import Cog, get_cogs
from principality.utils import url_to_json

from typer import Typer, run, Option
from typing import List
from superdict import SuperDict

class CogNotFound(Exception):
    pass

class PseudoCog():
    def __new__(self, url: str):
        self.url = url
        self.installed = False
        self.metadata = SuperDict()

    def install(self):
        self._install(self.url, self.directory)

    def _install(self, url: str, path: Path):
        if not url: url = self.url
        if self.installed: return

        files = url_to_json(url)
        for data in files:
            if data['type'] == 'dir':
                new_url = url+'/'+data['name']
                new_path = path/data['name']
                if not new_path.exists(): new_path.mkdir()
                self.install(url=new_url, path=new_path)
            elif data['type'] == 'file':
                if not path.exists(): path.mkdir()
                with urllib.request.urlopen(data['download_url']) as response, open(path/data['name'], 'wb') as file:
                    copyfileobj(response, file)

        self.installed = True

    def to_cog(self):
        if not self.installed: return CogNotFound("PseudoCog isn't installed")
        return get_cogs(self.directory)[0]

class Cherub(Configurable):
    """A Principality module manager."""

    config_file = 'configs/Bot.toml'

    class Config:
        module_repo_url: str = Option('https://api.github.com/repos/Soumeh/Principality-Next-Modules/contents/')
        default_requirements: List[str] = Option(["git+https://github.com/Soumeh/Principality-Next/principality", "git+https://github.com/Soumeh/Principality-Next/cherub"])

    def __init__(self):
        Configurable.__init__(self)

        self.requirements = self.config.default_requirements
        self.db = Local('cogs')
        self.db['dependencies'] = self.config.default_requirements
        self.dependencies = self.db['dependencies']
        self.db['cogs'] = {}
        self.cogs = self.db['cogs']

        self.cog_folder = Path(self.config.cog_folder)
        #if not cog_folder.exists(): cog_folder.mkdir()

        #for cog in get_cogs(cog_folder):
        #    self.cogs[cog.__name__] = cog

    def save_requirements(self):
        with open('requirements.txt', 'w') as file:
            file.write('\n'.join(self.requirements))

    def cogs_from_module(self, module):
        cogs = []
        for cog in [c[1] for c in getmembers(module, isclass)]:
            if issubclass(cog, Cog) and cog != Cog:
                cogs.append(cog)
        return cogs

    def _cog_installed(self, cog: str):
        return cog.lower() in self.cogs
    
    def _cog_exists(self, cog: str):
        pass

    def update(self: None, arguments):
        pass

    def check(self, cog: str):
        installed = self._cog_installed(cog)
        if not installed: return print(f"Cog '{cog}' is not installed or can't be found")
        # TODO actual delete code

    def delete(self, cog: str, delete_data: bool = True, delete_config: bool = False):
        installed = self._cog_installed(cog)
        if not installed: return print(f"Cog '{cog}' is not installed or can't be found")
        # TODO actual delete code

    def install(cog: str):
        self._cog_exists(cog)

        installed = self._cog_installed(cog)
        if installed: return print(f"Cog '{cog}' is already installed")

        cog_url = self.config.module_repo_url + cog
        cog_folder = self.cog_folder / cog
        prepared_cog = PseudoCog(cog_url, cog_folder)
        prepared_cog.install()

        # get requirements
        if 'dependencies' in installed_cog.metadata:
            dependencies = [i.after('@ ') for i in installed_cog.metadata['dependencies']]
            self.requirements.extend(dependencies)

        self.save_requirements()

    def installed_cogs(self) -> List[Cog]:
        return self.cogs.keys()

    def available_cogs(self):
        pass

    #with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
    #    shutil.copyfileobj(response, out_file)

    #if args.install:
    #    chrb.install(args.install)

    #if args.configure:
    #    pass

    #if args.remove:
    #    confirm = input(f"Are you sure that you want to delete the module(s) '{args.remove}'? (y/n): ")
    #    if is_true(confirm):
    #        chrb.delete(args.remove)
    #        print(f"Removed module '{args.remove}'")
    #        remove_config = input(f"Would you also like to remove the configuration file(s) for the module(s)? (y/n): ")
    #        if is_true(remove_config):
    #            chrb.delete_config()

    #if args.update:
    #    chrb.remove(args.update)

    #if args.list:
    #    print('Installed Modules:')
    #    print('\n'.join(chrb.cogs.keys()))