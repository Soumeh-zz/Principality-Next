from typer import Typer
from os import getenv
from dotenv import load_dotenv

app = Typer(pretty_exceptions_show_locals=False, pretty_exceptions_short=True)
load_dotenv()

@app.command()
def start(dev_mode: bool = False):

    if dev_mode:
        from principality import PrincipalityDev
        client = PrincipalityDev()
    else:
        from principality import Principality
        client = Principality()

    token = getenv(client.config.token_env_var)
    if not token:
        print("A Discord bot token must be provided in an environmental variable in order to start.")
    else:
        client.load()
        client.run(token)

@app.command()
def info():
    pass

if __name__ == '__main__':
    app()
