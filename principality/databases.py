from pathlib import Path
from json import dump, load
from typing import List, Any
from os import getenv
from dotenv import load_dotenv
from superdict import SuperDict
from collections import UserDict
from shutil import rmtree

from pyfigure import Configurable, Option

load_dotenv()

# files

class TempFiles():

    def __str__(self):
        return str(self.list())

    def __init__(self):
        self._files = {}

    def save(self, bytes: bytearray, path: Path):
        """Save a file to the database at a specific location

        Args:
            bytes (bytearray): File bytes to store
            path (Path): Location to store the file to
        """
        self._files[path] = bytes

    def load(self, path: Path) -> bytearray:
        """Load a file from the database at a specific location

        Args:
            path (Path): Location of the file

        Returns:
            bytearray: The bytes of the file
            None: Only if the file doesn't exist
        """
        return self._files.get(path, None)

    def contains(self, path: Path) -> bool:
        """Check whether or not a file exists in the database at a specific location

        Args:
            path (Path): Location of the file

        Returns:
            bool: Whether or not the file exists
        """
        return path in self._files.keys()

    def list(self) -> List[str]:
        """Get all files in the database

        Returns:
            List[str]: A list of all file paths
        """
        return self._files.keys()

    def delete(self, path: Path):
        """Delete a file from the database at a specific location

        Args:
            path (Path): Location of the file
        """
        try:
            del self._files[path]
        except:
            pass

class LocalFiles(TempFiles):

    def __init__(self, directory):
        super().__init__()
        self._directory = directory
        if not self._directory.exists(): self._directory.mkdir()

    def save(self, bytes, path):
        with open(self._directory / path, 'wb') as file:
            file.write(bytes)

    def load(self, path):
        with open(self._directory / path, 'rb') as file:
            return file.read()

    def contains(self, path):
        return (self._directory/path).exists()

    def list(self):
        return [i.name for i in self._directory.iterdir()]

    def delete(self, path):
        (self._directory/path).unlink(True)

class DataDrive(TempFiles):

    def __init__(self, drive):
        super().__init__()
        self._drive = drive

    def save(self, bytes, path):
        self._drive.put(str(path), bytes)

    def load(self, path):
        self._drive.get(str(path))

    def contains(self, path):
        return path in self.list()

    def list(self):
        return self._drive.list()['names']
    
    def delete(self, path):
        self._drive.delete(path)

# json

class TempData(UserDict):
    pass

class LocalData(TempData):

    def __init__(self, file: Path, *args):
        if not file.exists():
            with open(file, 'w') as w_file:
                w_file.write('{}')
        self._file = file
        with open(file, 'r') as r_file:
            super().__init__(load(r_file))

    def dump(self):
        """Save the JSON content of the database."""
        with open(self._file, 'w+') as file:
            dump(dict(self), file, separators=(',', ':'))

class DetaBase(TempData):

    def __init__(self, base, *args):
        super().__init__(self, *args)
        self._base = base

    def __setitem__(self, key, value):
        self._base.put(value, key)

    def __getitem__(self, key):
        r = self._base.get(key)
        if r: return r['value']
    
    def __contains__(self, key):
        if self._base.get(key): return True
        else: return False

    def __delitem__(self, key):
        self._base.delete(key)

# databases

class Database():
    """Store data persistantly (in some cases)

    Args:
        name (str): Name of the database.
    """

    def clear(self):
        """Completely delete the database"""
        if not self.clear_confirmation:
            self.clear_confirmation = True
            return
        pass

    def __init__(self, name: str):
        self.data = TempData()
        self.files = TempFiles()
        self.clear_confirmation = False

class Deta(Database, Configurable):

    config_file = Path('configs/Bot.toml')

    class Config:
        deta_token_env_var: str = Option('DETA_TOKEN', "The environmental variable of your bot's token. (Leave as default unless you want to work with multiple bots)")
        deta_token: str = Option('', description='In case you are using a Deta Base, provide your API key here')

    def clear(self):
        if not self.clear_confirmation:
            self.clear_confirmation = True
            return
        

    def __init__(self, name):
        Configurable.__init__(self)
        from deta import Deta

        token = getenv(self.config.deta_token_env_var, None)
        if not token:
            raise AttributeError('You must provide a Deta API key in the bot configuration file if you want to use Deta Bases')

        deta = Deta(token)
        self.data = DetaBase(deta.Base(name))
        self.files = DetaDrive(deta.Drive(name))

class Local(Database, Configurable):

    config_file = Path('configs/Database.toml')
    
    class Config:
        database_directory: str = Option('data/', 'What directory to store database data in')

    def clear(self):
        if not self.clear_confirmation:
            self.clear_confirmation = True
            return
        rmtree(self.data._file)
        rmtree(self.files._directory)

    def __init__(self, name):
        Configurable.__init__(self)

        data_dir = Path(self.config.database_directory)
        if not data_dir.exists(): data_dir.mkdir()
        
        this_dir = data_dir/name
        self.data = LocalData(this_dir.with_suffix('.json'))
        self.files = LocalFiles(this_dir)

databases = {
    'deta': Deta,
    'temp': Database,
    'local': Local
}

def get_db(type, name: str) -> Database:
    return databases[type.lower()](name)