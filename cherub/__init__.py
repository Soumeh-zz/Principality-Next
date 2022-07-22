from importlib import import_module
from inspect import getmembers, isclass
from tomlkit import loads
from pathlib import Path
from shutil import copyfileobj
from sys import argv, modules
from urllib.error import HTTPError
import urllib.request
from os import getenv
from requests import get

from typing import List

from pyfigure import Configurable, Option
from principality.databases import Local
from principality.cog import Cog, get_cogs
from principality.utils import url_to_json

from typing import List
from superdict import SuperDict

class CogNotFound(Exception):
    pass

class GithubCog():
    def __init__(self, url: str, path: Path, github_headers: dict = {}):
        self.url = url
        self.installed = False
        self.directory = path
        self.github_headers = github_headers

    def gen_metadata(self):
        if hasattr(self, 'metadata'): return self.metadata
        files = url_to_json(self.url, self.github_headers)
        req = get([file for file in files if file['name'] == 'pyproject.toml'][0]['download_url'], headers=self.github_headers)
        pyproject = loads(req.text)
        self.metadata = SuperDict(pyproject['project'])
        return self.metadata

    def install(self):
        self._install(self.url, self.directory)
        #return Cog.from_dir(path=self.directory)

    def _install(self, url: str, path: Path):
        if not url: url = self.url
        if self.installed: return

        files = url_to_json(url, self.github_headers)
        for data in files:
            if data['type'] == 'dir':
                new_url = url+'/'+data['name']
                new_path = path/data['name']
                if not new_path.exists(): new_path.mkdir()
                self._install(new_url, new_path)
            elif data['type'] == 'file':
                if not path.exists(): path.mkdir()
                with urllib.request.urlopen(data['download_url']) as response, open(path/data['name'], 'wb') as file:
                    copyfileobj(response, file)

        self.installed = True

class Cherub(Configurable):
    """A Principality module manager."""

    config_file = 'configs/Bot.toml'

    class Config:
        module_repo_url: str = Option('https://api.github.com/repos/Soumeh/Principality-Next-Modules/')

    def __init__(self):
        Configurable.__init__(self)

        if getenv('GITHUB_TOKEN', None): 
            self.github_headers = {"Authorization": f"{getenv('GITHUB_TOKEN')} OAUTH-TOKEN"}
        else:
            self.github_headers = {}

        self.cog_folder = Path(self.config.cog_folder)
        if not self.cog_folder.exists(): self.cog_folder.mkdir()

        self.populate()

    def populate(self):
        self.dependencies = []
        self.cogs = {}
        for id, cog in get_cogs(self.cog_folder).items():
            cog = cog()
            self.cogs[id] = cog.metadata.version or None
            if 'dependencies' in cog.metadata:
                for dep in cog.metadata['dependencies']:
                    if '@ ' in dep: dep = dep.rsplit('@ ', 1)[1]
                    self.dependencies.append(dep)

    def save_requirements(self):
        with open('cog_requirements.txt', 'w') as file:
            file.write('\n'.join(set(self.dependencies)))

    def _cog_installed(self, cog: str):
        return cog.lower() in self.cogs
    
    def _cog_exists(self, cog: str):
        if not hasattr(self, 'available'):
            data = url_to_json(self.config.module_repo_url+'contents/cogs/', self.github_headers)
            self.available = [i['name'] for i in data if i['type'] == 'dir']
        return cog in self.available

    def install(self, cog: str):
        if not self._cog_exists(cog): return print(f"Cog '{cog}' does not exist")
        if self._cog_installed(cog): return print(f"Cog '{cog}' is already installed")

        cog_url = self.config.module_repo_url + 'contents/cogs/' + cog
        cog_folder = self.cog_folder / cog
        prepared_cog = GithubCog(cog_url, cog_folder, self.github_headers)
        prepared_cog.install()

        # get requirements
        if 'dependencies' in prepared_cog.metadata:
            [self.dependencies.append(i.after('@ ')) for i in prepared_cog.metadata['dependencies']]

        self.save_requirements()
        print(f"Installed cog '{cog}'")

    def update(self: None, cog: str):
        if not self._cog_installed(cog): return print(f"Cog '{cog}' is not installed")
        #if not self._cog_exists(cog): return print(f"Cog '{cog}' does not exist")

        cog_url = self.config.module_repo_url + 'contents/' + cog
        cog_folder = self.cog_folder / cog
        prepared_cog = GithubCog(cog_url, cog_folder, self.github_headers)
        prepared_cog.gen_metadata()
        if self.cogs[cog.lower()] == prepared_cog.metadata.version:
            return print(f"Cog '{cog}' is already up to date")
        prepared_cog.install()

        # get requirements
        if 'dependencies' in prepared_cog.metadata:
            [self.dependencies.append(i.after('@ ')) for i in prepared_cog.metadata['dependencies']]

        self.save_requirements()
        print(f"Updated cog '{cog}'")

    def check(self, cog: str):
        installed = self._cog_installed(cog)
        if not installed: return print(f"Cog '{cog}' is not installed or can't be found")
        # TODO actual delete code

    def delete(self, cog: str, delete_data: bool = True, delete_config: bool = False):
        installed = self._cog_installed(cog)
        if not installed: return print(f"Cog '{cog}' is not installed or can't be found")
        # TODO actual delete code