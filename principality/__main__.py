from typer import run, Option
from os import getenv, getcwd, path
from dotenv import load_dotenv

load_dotenv()

def main(dev_mode: bool = False):

    if dev_mode:
        from principality import PrincipalityDev
        client = PrincipalityDev()
    else:
        from principality import Principality
        client = Principality()

    token = getenv(client.config.token_env_var)
    print(token)
    print(client.config.token_env_var)
    print(getcwd())
    print(path.dirname(path.realpath(__file__)))
    if not token:
        print("A Discord bot token must be provided in an environmental variable in order to start.")
    else:
        client.run(token)

if __name__ == '__main__':
    run(main)
