from importlib import import_module, reload
from pathlib import Path

from nextcord.ext import tasks
from bot import Principality
from overseer import Overseer

class PrincipalityDev(Principality):

    async def on_ready(self):
        await super().on_ready()
        self.config_overseer = Overseer(self.config_folder, '*.toml')
        self.cog_overseer = Overseer(Path(self.config['cog_folder']), ['**/*.py', '**/*.json'])
        await self.update_checker.start()



    @tasks.loop(seconds=5)
    async def update_checker(self):

        # check configs
        changed, added, removed = self.config_overseer.changes()

        for file in changed.union(removed):
            file_name = file.stem
            cog_folder = Path(self.config['cog_folder']) / file_name
            module = import_module(Path(self.config['cog_folder']).stem+'.'+file_name)
            for temp_cog in self.cogs_from_module(module):
                cog_name = temp_cog().__cog_name__
                cog = self.cogs[cog_name]
                cog.reload_config()
                print(f"Reloaded config for cog '{cog_name}'")

        # check cogs
        changed, added, removed = self.cog_overseer.changes()
        functions = {'changed': changed, 'added': added, 'removed': removed}

        for function, list in functions.items():
            for file in list:
                file_name = file.parent.stem
                cog_folder = Path(self.config['cog_folder']) / file_name

                module = import_module(Path(self.config['cog_folder']).stem+'.'+file_name)
                if function == 'changed':
                    reload(module)

                for cog in self.cogs_from_module(module):
                    cog = cog()
                    if function != 'removed':
                        await self.load_cog(cog, cog_folder)
                        await self.async_load_cog(cog)
                    else:
                        await self.unload_cog(cog)
