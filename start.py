from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser(description='Startup the bot.')
    parser.add_argument('--dev', action='store_true', help='Start the bot in development mode.')
    dev_mode = parser.parse_args().dev

    if dev_mode:
        from principality import PrincipalityDev
        client = PrincipalityDev()
    else:
        from principality import Principality
        client = Principality()

    token = client.config.token
    if not token:
        print("A Discord bot token must be provided in configs/Bot.toml in order to start")
    else:
        client.run(client.config.token)
