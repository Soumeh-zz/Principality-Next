from pathlib import Path
from json import dump, load
from typing import List, Any
from os import getenv
from dotenv import load_dotenv
from superdict import SuperDict

from pyfigure import Configurable, Option

load_dotenv()

class Database():

    def save(self, bytes: bytearray, path: Path):
        """Save a file to the database at a specific location

        Args:
            bytes (bytearray): File bytes to store
            path (Path): Location to store the file to
        """
        pass

    def load(self, path: Path) -> bytearray:
        """Load a file from the database at a specific location

        Args:
            path (Path): Location of the file

        Returns:
            bytearray: The bytes of the file
            None: Only if the file doesn't exist
        """
        pass

    def contains(self, path: Path) -> bool:
        """Check whether or not a file exists in the database at a specific location

        Args:
            path (Path): Location of the file

        Returns:
            bool: Whether or not the file exists
        """
        pass

    def list(self) -> List[str]:
        """Get all files in the database

        Returns:
            List[str]: A list of all file paths
        """
        pass

    def delete(self, path: Path):
        """Delete a file from the database at a specific location

        Args:
            path (Path): Location of the file
        """
        pass

    def __setitem__(self, key: str, value: Any):
        pass

    def __getitem__(self, key: str) -> Any:
        pass

    def __contains__(self, key: str) -> bool:
        pass

    def __delitem__(self, key: str):
        pass

class Deta(Database, Configurable):

    config_file = Path('configs/Bot.toml')

    class Config:
        deta_token_env_var: str = Option('DETA_TOKEN', "The environmental variable of your bot's token. (Leave as default unless you want to work with multiple bots)")
        deta_token: str = Option('', description='In case you are using a Deta Base, provide your API key here')

    def __init__(self, name):
        Configurable.__init__(self)
        from deta import Deta

        token = getenv(self.config.deta_token_env_var, None)
        if not token:
            raise AttributeError('You must provide a Deta API key in the bot configuration file if you want to use Deta Bases')
        deta = Deta(token)
        self.base = deta.Base(name)
        self.drive = deta.Drive(name)
    
    def save(self, bytes, path):
        self.drive.put(str(path), bytes)

    def load(self, path):
        self.drive.get(str(path))

    def contains(self, path):
        return path in self.list()

    def list(self):
        return self.drive.list()['names']
    
    def delete(self, path):
        self.drive.delete(path)

    def __setitem__(self, key, value):
        self.base.put(value, key)

    def __getitem__(self, key):
        r = self.base.get(key)
        if r: return r['value']
    
    def __contains__(self, key):
        if self.base.get(key): return True
        else: return False

    def __delitem__(self, key):
        self.base.delete(key)

class Local(Database, dict, Configurable):

    config_file = Path('configs/Database.toml')
    
    class Config:
        database_directory: str = Option('data/', 'What directory to store database data in')

    def __init__(self, name):
        Configurable.__init__(self)

        data_dir = Path(self.config.database_directory)
        if not data_dir.exists(): data_dir.mkdir()

        self.directory = data_dir/name
        if not self.directory.exists(): self.directory.mkdir()

        self.file = data_dir/f'{name}.json'
        if not self.file.exists():
            with open(self.file, 'w') as file:
                file.write('{}')

        self._load_from_file()

    def save(self, bytes, path):
        with open(self.directory / path, 'wb') as file:
            file.write(bytes)

    def load(self, path):
        with open(self.directory / path, 'rb') as file:
            return file.read()

    def contains(self, path):
        return (self.directory/path).exists()

    def list(self):
        return [i.name for i in self.directory.iterdir()]

    def delete(self, path):
        (self.directory/path).unlink(True)
    
    def _load_from_file(self):
        with open(self.file, 'r') as file:
            self.__json__ = load(file) or {}

    def save_json(self):
        with open(self.file, 'w+') as file:
            dump(self.__json__, file, separators=(',', ':'))

class Temp(dict, Database):
    
    def __init__(self, name):
        self.files = {}

    def save(self, bytes, path):
        self.files[path] = bytes

    def load(self, path):
        return self.files.get(path, None)
    
    def contains(self, path):
        return path in self.files.keys()
    
    def delete(self, path):
        try:
            del self.files[path]
        except:
            pass

    def list(self):
        return [i for i in self.files.keys()]

databases = {
    'deta': Deta,
    'temp': Temp,
    'local': Local
}

def get_db(type, name: str) -> Database:
    return databases[type.lower()](name)