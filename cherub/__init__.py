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
from shutil import rmtree
from json.decoder import JSONDecodeError

from typing import List

from pyfigure import Configurable, Option
from principality import Principality
from principality.databases import Local
from principality.cog import Cog, get_cogs
from principality.utils import url_to_json

from typing import List
from superdict import SuperDict

class Ratelimit(Exception):
    pass

class CogNotFound(Exception):
    pass

def _github_download(url: str, headers: dict = {}):
    result = url_to_json(url, headers)
    if 'documentation_url' in result:
        raise Ratelimit("You are being rate limited by Github, if you haven't provided a github token, please wait and try again")
    return result

class GithubCog():
    def __init__(self, url: str, path: Path, github_headers: dict = {}):
        self.url = url
        self.directory = path
        self.github_headers = github_headers
        self.installed = False

    def install(self):
        self._install(self.url, self.directory)
        cog = Cog.from_dir(path=self.directory)
        return cog()

    def _get_files(self, url: str, path: Path, container: list):
        files = _github_download(url=url, headers=self.github_headers)
        self.file_data = []
        for data in files:
            if data['type'] == 'dir':
                new_url = url+'/'+data['name']
                new_path = path/data['name']
                if not new_path.exists(): new_path.mkdir()
                self._get_files(new_url, new_path, container)
            elif data['type'] == 'file':
                if not path.exists(): path.mkdir()
                container.append( [data['download_url'], path/data['name']] )

    def _install(self, url: str, path: Path):
        if self.installed: return

        file_data = []
        self._get_files(url, path, file_data)

        for file_url, file_path in file_data:
            with urllib.request.urlopen(file_url) as response, open(file_path, 'wb') as file:
                copyfileobj(response, file)

        self.installed = True

class Cherub(Configurable):
    """A Principality module manager."""

    config_file = 'configs/Bot.toml'

    class Config:
        module_repo_url: str = Option('https://api.github.com/repos/Soumeh/Principality-Next-Modules/')
        cog_folder: str = Option('cogs', "What directory to load modules from")

    def __init__(self):

        self.db = Local('Cogs')
        Configurable.__init__(self)
        Principality()

        self.cog_folder = Path(self.config.cog_folder)
        if not self.cog_folder.exists(): self.cog_folder.mkdir()

        populate = False
        if 'cogs' not in self.db.data:
            self.db.data['cogs'] = {}
            populate = True
        if 'dependencies' not in self.db.data:
            with open('cog_requirements.txt') as file:
                self.db.data['dependencies'] = [i for i in file.read().split('\n') if i]
        self.dependencies = self.db.data['dependencies']
        self.cogs = self.db.data['cogs']

        if populate:
            self.populate()
            self.db.data.dump()

        if getenv('GITHUB_TOKEN', None): 
            self.github_headers = {"Authorization": f"token {getenv('GITHUB_TOKEN')}"}
        else:
            self.github_headers = {}

        self.cog_folder = Path(self.config.cog_folder)
        if not self.cog_folder.exists(): self.cog_folder.mkdir()
        #self.populate()

    def _save(self):
        self.db.data.dump()
        with open('cog_requirements.txt', 'w') as file:
            file.write('\n'.join(set(self.dependencies)))

    def _cog_installed(self, cog: str):
        return cog in self.cogs
    
    def _github_download(self, url: str, headers: dict = {}):
        print(url)
        result = url_to_json(url, headers)
        if 'documentation_url' in result:
            raise Ratelimit("You are being rate limited by Github, if you haven't provided a github token, please wait and try again")
        return result

    def _cog_exists(self, cog: str):
        if not hasattr(self, 'available_cogs'):
            data = _github_download(self.config.module_repo_url+'contents/cogs/', self.github_headers)
            self.available_cogs = [i['name'] for i in data if i['type'] == 'dir']
        return cog in self.available_cogs

    def populate(self):
        for id, cog in get_cogs(self.cog_folder).items():
            if id in self.cogs: return
            cog = cog()
            self.cogs[id] = {
                'name': str(cog.name),
                'version': str(cog.metadata.version),
                'directory': str(cog.directory),
                'config_file': str(cog.config_file)
            }
            #if hasattr(cog, 'db'):
            #    self.cogs[id].update({
            #        'db_file': blah,
            #        'db_dir': blah
            #    })
            if 'dependencies' in cog.metadata:
                for dep in cog.metadata['dependencies']:
                    if '@ ' in dep: dep = dep.rsplit('@ ', 1)[1]
                    self.dependencies.append(dep)
        self._save()
        print(f"Populated cogs")

    def install(self, cog: str):
        cog = cog.lower()
        if self._cog_installed(cog): return print(f"Cog '{cog}' is already installed")
        if not self._cog_exists(cog): return print(f"Cog '{cog}' does not exist")

        cog_url = self.config.module_repo_url + 'contents/cogs/' + cog
        cog_folder = self.cog_folder / cog
        prepared_cog = GithubCog(cog_url, cog_folder, self.github_headers)
        installed_cog = prepared_cog.install()

        self.cogs[cog] = {
            'name': str(installed_cog.name),
            'version': str(installed_cog.metadata.version),
            'directory': str(installed_cog.directory),
            'config_file': str(installed_cog.config_file)
        }

        # get requirements
        if 'dependencies' in installed_cog.metadata:
            [self.dependencies.append(i.after('@ ')) for i in installed_cog.metadata['dependencies']]

        self._save()
        print(f"Installed cog '{cog}'")

    def update(self: None, cog: str):
        cog = cog.lower()
        if not self._cog_installed(cog): return print(f"Cog '{cog}' is not installed")
        if not self._cog_exists(cog): return print(f"Cog '{cog}' does not exist")

        cog_url = self.config.module_repo_url + 'contents/' + cog
        cog_folder = self.cog_folder / cog
        prepared_cog = GithubCog(cog_url, cog_folder, self.github_headers)
        if self.cogs[cog.lower()]['version'] == prepared_cog.metadata.version:
            return print(f"Cog '{cog}' is up to date")
        installed_cog = prepared_cog.install()

        self.cogs[cog] = {
            'name': str(installed_cog.name),
            'version': str(installed_cog.metadata.version),
            'directory': str(installed_cog.directory),
            'config_file': str(installed_cog.config_file)
        }

        # get requirements
        if 'dependencies' in installed_cog.metadata:
            [self.dependencies.append(i.after('@ ')) for i in prepared_cog.metadata['dependencies']]

        self._save()
        print(f"Updated cog '{cog}'")

    def delete(self, cog: str, delete_data: bool = True, delete_config: bool = False):
        cog = cog.lower()
        if not self._cog_installed(cog): return print(f"Cog '{cog}' is not installed")
        # TODO actual delete code
        rmtree(Path(self.cogs[cog]['directory']).parent)
        if delete_config: Path(self.cogs[cog]['config_file']).unlink()
        #if delete_data:
        #    if hasattr(cog, 'db'):
        #        cog.db.clear()
        #        confirm = is_true(input("Are you sure that you want to delete the Cog's data? This cannot be reversed (y/n) "))
        #        if confirm: cog.db.clear()

        del self.cogs[cog]
        self._save()
        print(f"Deleted cog '{cog}'")

def is_true(val):
    if val.lower() in ('y', 'yes', 't', 'true', 'on', '1'):
        return True