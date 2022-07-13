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
from cog import Cog

class Cherub(Configurable):
    """A Principality module manager."""

    config_file = 'configs/Bot.toml'

    from argument_parser import Argument_Parser
    parser = Argument_Parser()

    class Config:
        module_repo_url: str = Option('https://api.github.com/repos/Soumeh/Principality-Next-Modules/contents/')
        default_requirements: List[str] = Option(["nextcord", "python-dotenv", "pyfigure"])

    def __init__(self):
        Configurable.__init__(self)

        self.requirements = self.config.default_requirements
        self.cogs = {}

        if not Path(self.config['cog_folder']).exists():
            Path(self.config['cog_folder']).mkdir()

        for cog_folder in Path(self.config['cog_folder']).iterdir():
            if cog_folder.is_dir() and not cog_folder.stem.startswith('.') and not cog_folder.stem.startswith('__'):
                print(f"{self.config['cog_folder']}.{cog_folder.stem}.src.{cog_folder.stem}")
                module = import_module(f"{self.config['cog_folder']}.{cog_folder.stem}.src.{cog_folder.stem}")
                for cog in self.cogs_from_module(module):
                    cog = cog()
                    self.cogs[cog.__class__.__name__] = cog
        
        self.parser.parse(argv)

    @parser.argument()
    def update(self, arguments):
        pass

    @parser.argument()
    def check(self, arguments):
        pass

    @parser.argument()
    def delete(self, arguments):
        print(modules[self.__class__.__module__].__file__)
    
    @parser.argument()
    def list(self, arguments):
        """List locally installed and available cogs."""
        subcommand = arguments[0] if arguments else None
        if subcommand in ['installed', 'i']:
            print('Installed Modules:')
            print('\n'.join(self.cogs.keys()))
        if subcommand in ['available', 'a']:
            print('w.i.p')
        else:
            print('w.i.p')
    
    #@list.subcommand()
    #def installed(self):
    #    pass
    
    #@list.subcommand()
    #def available(self):
    #    pass

    def delete_config(self, cog):
        Path(cog.config_file).rmdir()

    def save_requirements(self):
        with open('requirements.txt', 'w') as file:
            file.write('\n'.join(self.requirements))

    def cogs_from_module(self, module):
        cogs = []
        for cog in [c[1] for c in getmembers(module, isclass)]:
            if issubclass(cog, Cog) and cog != Cog:
                cogs.append(cog)
        return cogs

    @parser.argument()
    def install(self, cogs):
        """Install cog(s). Space separated."""

        installed = False
        for cog in cogs:
            cog = cog.lower()
            for installed_cog in self.cogs.keys():
                if cog == installed_cog.lower(): return print(f"Cog '{installed_cog}' is already installed")
            cog_url = self.config.module_repo_url + cog
            try:
                self.github_download(cog_url, Path('cogs')/cog)
                installed = True
            except HTTPError:
                return print(f"Could not find cog named '{cog}'")

        if not installed: return
        module = import_module(self.config['cog_folder']+'.'+cog)
        cogs = self.cogs_from_module(module)
        cogs = [cog() for cog in cogs]

        # get requirements
        for cog in cogs:
            if 'install_requires' in cog.metadata:
                requirements = [i for i in cog.metadata['install_requires'].split('\n') if i]
                self.requirements.extend(requirements)

        self.save_requirements()

        #with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        #    shutil.copyfileobj(response, out_file)

    def github_download(self, url, path):
        with urllib.request.urlopen(url) as r:
            files = loads(r.read().decode())
        for data in files:
            if data['type'] == 'dir':
                new_url = url+'/'+data['name']
                new_path = path/data['name']
                if not new_path.exists(): new_path.mkdir()
                self.github_download(new_url, new_path)
            elif data['type'] == 'file':
                if not path.exists(): path.mkdir()
                with urllib.request.urlopen(data['download_url']) as response, open(path/data['name'], 'wb') as file:
                    copyfileobj(response, file)

def is_true(value: str) -> bool:
    """Check whether or not a string value is true."""
    return value in ['true', 't', 'yes', 'y', '1']

if __name__ == '__main__':
    Cherub()

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