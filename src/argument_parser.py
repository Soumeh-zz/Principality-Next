from typing import Callable, List

class Argument_Parser:

    def __init__(self):

        self.commands = {}
        self.shorthands = {}

        @self.argument()
        def help(self, args):
            longest_command = max([len(command) for command in self.commands.keys()])

            print("usage: python cherub.py [-c cmd] [arg] ...")

            for name, command in self.commands.items():
                length = longest_command-len(name)
                description = command.function.__doc__
                if description: description = f"\n{' '*(length+9)}".join(description.split('\n'))
                else: description = 'No description set.'
                print(f"{command.shorthand} {name}{' '*length}: {description}")

    def parse(self, args: list = []):

        if len(args) < 1:            
            command_name = 'help'
            arguments = []
        else: 
            command_name = args[0]
            arguments = args[1:]

        # check for command
        if command_name in self.commands:
            command = self.commands[command_name]
        # or for shorthand
        elif command_name in self.shorthands:
            command = self.shorthands[command_name]
        # stop if none found
        else:
            return print('Unknown command.')

        command.function(self, arguments)

    def argument(self, name: str = None, aliases: list = [], shorthand: str = None) -> Callable:
        
        def decorator(function: Callable):

            command = Command(self.commands, self.shorthands, function, name, aliases, shorthand)
            if not hasattr(command, 'name'): return function

            if command.shorthand != '  ':
                self.shorthands[command.shorthand] = command
            self.commands[command.name] = command
            for alias in command.aliases:
                self.commands[alias] = command
            return function

        return decorator

#class Command_Function(function):
#    pass

class Command(Argument_Parser):

    def __init__(self,
        commands: List[str],
        shorthands: List[str],

        function: Callable,
        name: str = None,
        aliases: List[str] = [],
        shorthand: str = None
    ):
        name = name or function.__name__
        shorthand = shorthand or '-'+name[0]

        if name in commands:
            print(f"Command named '{name}' already exists, define a new name in as a decorator argument.")
            return None

        if shorthand in shorthands:
            shorthand = shorthand.upper()
        if shorthand in shorthands:
            print(f"Shorthand '{shorthand}' already exists, define a new one by adding a shorthand to the argument decorator.")
            shorthand = '  '
        
        self.name = name
        self.shorthand = shorthand
        self.aliases = aliases
        self.function = function

if __name__ == '__main__':
    ap = Argument_Parser()
    ap.parse(['help'])