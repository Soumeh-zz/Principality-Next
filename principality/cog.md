# Cogs

Cogs are...

### Example Directory

```
example/
├── src/
│   └── example.py
├── pyproject.toml
└── readme.md (optional)
```

> You can download an example module [here](https://downgit.github.io/#/home?url=https://github.com/Soumeh/Principality-Next-Cogs/tree/master/example).

Each file has specific usages, which are described here:
- [pyproject.toml](#pyproject.toml)
- [readme.md](#readme.md)
- [example.py](#example.py)

# pyproject.toml

A [PEP 621](https://peps.python.org/pep-0621/) compatible project file, required to store your project's metadata, such as the display name, description, or version.

### Example File

`pyproject.toml`
```toml
[project]
name = "Example"
description = "Example Module."
version = "1.0"
authors = [
    { name = "Soumeh" }
]
# optional
readme = "readme.md"
```

# readme.md

W.I.P.

# example.py

A cog is initiated by making a new class that inherits the `principality.cog.Cog` class.

```py
from principality.cog import Cog

class Example(Cog):
    pass
```

> It's recommended to only have one cog class per cog, but if you have multiple classes, they'll all share the same metadata and configuration file.

To give the cog functionality, you can use these objects:
- [Configuration](#configuration)
- [Loaded Method](#loaded-method)
- [Ready Method](#ready-method)
- [Listeners](#listeners)
- [Commands](#commands)

## Configuration

Cogs are configurable using the [pyfigure](https://pypi.org/project/pyfigure/) library, which means that all you need to make configurable variables is a `Config` class inside of the cog.

```py
class Config:
    is_true: bool = ConfigOption(True, "Whether or not this value is true")
```

> You can only have one `Config` class, but you can make new classes in the `Config` class to make nested config options.

```py
class Config:
    main_value: str = ConfigOption('main', "The main configuration value")
    class sub_config:
        sub_value: str = ConfigOption('main', "A secondary configuration value")
```

Users can then change the value of the config value inside of the config directory (`configs/` by default), in the cog's file (`configs/Example.toml` in this case).

> Values are automatically type checked and parsed by the library.

When the cog is loaded, it'll have a new attribute named `config` (accessible with `self.config`), which, in this case, returns `{'is_true': True}` by default, but changes depending on what the user changed it into.

Config values can also be accessed as an attribute. (Including subvalues)
```py
>>> this.config['is_true']
# True
>>> this.config.is_true
# True
```

> For more information about configuration files, visit the [pyfigure](https://pypi.org/project/pyfigure/) documentation.

## Loaded Method

The `load()` method is called once the bot has loaded the cog, and is intended to be an alternative to the `__init__()` magic method.

```py
def load(self):
    print('Loaded!')
```

> You can only have one `load()` method.

This method is called before the bot is async ready, so use the `ready()` method in case you want to initiate the cog with information only accessible by the bot.

## Ready Method

The `ready()` method is called once the bot is fully loaded and async ready, giving you access to data only accessible by bot such as member roles or server members.

```py
async def ready(self):
    print('Async Loaded!')
```

> You can only have one `ready()` method.

## Listeners

Listeners are methods, with the `Cog.listener()` decorator, that get called when a certain event happens on Discord.

The event which is listened for is defined as the method's name by default, but can be overrided by adding a string to the method's decorator.

```py
@Cog.listener()
async def on_member_join(self, member):
    print(f"{member.mention} has joined {member.guild.name}")
```

The event which is listened for is defined as the method's name by default, but can be overrided by adding the 

```py
@Cog.listener('on_member_join')
async def my_listener(self, member):
    print(f"{member.mention} has joined {member.guild.name}")
```

Note, the arguments of the listener method change based on which event it's listening to.

> A list of events can be found [here](https://docs.nextcord.dev/en/stable/api.html#discord-api-events).

## Commands

Commands can either be [regular commands](https://docs.nextcord.dev/en/stable/ext/commands/commands.html), [slash commands](https://docs.nextcord.dev/en/stable/interactions.html?highlight=slash%20commands#simple-slash-command-example), [user commands](https://docs.nextcord.dev/en/stable/interactions.html?highlight=slash%20commands#user-commands) or [message commands](https://docs.nextcord.dev/en/stable/interactions.html?highlight=slash%20commands#message-commands), all accessible using the `Cog.command()`, `Cog.slash_command()`, `Cog.user_command()` and `Cog.message_command()` decorators accordingly.

> Only slash commands will be covered, and will be referred to as just commands.

Commands are methods, decorated with `Cog.slash_command()`, that get called whenever a user initiates a command with the same name as the command.

The name is the method's name by default, but can be changed by adding `name='command_name'` to the decorator.

```py
@Cog.slash_command()
async def ping(self, ctx: Interaction):
    await ctx.response.send_message("Pong!")
```

The `ctx` argument is a Nextcord [`Interaction`](https://docs.nextcord.dev/en/stable/api.html?highlight=interaction#nextcord.Interaction) object, which contains data about the command's execution.

> While debugging, it is recommended to add `guild_ids=[guild_id]` to the command's decorator, where `guild_id` is the id of the Discord server that you are debugging it in.  This will make changes made to the command get refreshed when reloaded.

### Example File

`example.py`
```py
from principality.cog import  Cog, ConfigOption, SlashOption

class Example(Cog):

    # Built-in attributes:
    # self.bot - Returns the Bot object that loaded this cog
    # self.directory - Returns the Path object of the folder containing this cog

    class Config:
        is_true: bool = ConfigOption(True, "Whether or not this value is true")

    def load(self):
        print('Loaded!')

    async def ready(self):
        print('Async Loaded!')

    @Cog.slash_command()
    async def ping(self, ctx: Interaction):
        await ctx.response.send_message("Pong!")

    @Cog.listener()
    async def on_member_join(self, member):
        print(f"{member.mention} has joined {member.guild.name}")
```