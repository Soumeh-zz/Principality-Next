from typer import Typer, Option
from os import getenv
from dotenv import load_dotenv
from asyncio import run

from nextcord.errors import PrivilegedIntentsRequired, LoginFailure
from principality.utils import url_to_json

app = Typer(pretty_exceptions_show_locals=False, pretty_exceptions_short=True)

@app.callback()
def main():
    pass

@app.command()
def start(dev_mode: bool = Option(False, "--dev", help="Start the bot in Development Mode")):
    """Start your Principality Bot"""

    if dev_mode:
        from principality import PrincipalityDev
        client = PrincipalityDev()
        print('Starting Principality in Development Mode...\n')
    else:
        from principality import Principality
        client = Principality()
        print('Starting Principality...\n')

    token = getenv(client.config.token_env_var)
    if not token:
        print("""To get started, you have to provide a Discord Bot token
If you have not made a Discord Bot or do not know how to get its token, follow this guide:
https://discordpy.readthedocs.io/en/stable/discord.html

This token is stored in the .env file, for future use
In case you enter an invalid token, you can change it inside of the .env file by replacing the text after TOKEN=\n""")
        token = input("Token: ")
        print('')
        if not token: return print("A Discord Bot token must be provided in order to start.")

        with open('.env', 'r') as file:
            env = file.read().split('\n')
        for val in env:
            if val.startswith('TOKEN='): env[env.index(val)] = 'TOKEN=' + token
        with open('.env', 'w') as file:
            file.write('\n'.join(env))

    try:
        client.load_cogs()
        run(client.run(token))
    except PrivilegedIntentsRequired as error:
        data = url_to_json('https://discordapp.com/api/oauth2/applications/@me', {'Authorization': 'Bot '+token})
        print(f"""Priviledged Gateway Intents have not been enabled for your bot, enable them so your bot can properly initialize
You can enable them here:
https://discord.com/developers/applications/{data["id"]}/bot""")
    except LoginFailure as error:
        print('You have provided an improper Discord Bot token, you can replace it with a proper one inside of the .env file')

@app.command()
def info():
    """W.I.P."""

@app.command()
def setup_heroku():
    """Set up all of the files necessary to host on Heroku"""
    with open('Procfile', 'w+') as file:
        file.write('worker: python -m principality start')
    with open('runtime.txt', 'w+') as file:
        file.write('python-3.10.5')
    print("Created Heroku files")

def main():
    load_dotenv('.env')
    app()

if __name__ == '__main__':
    from os import getcwd
    main()
