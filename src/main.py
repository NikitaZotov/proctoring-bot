import configparser

from bot_starter import BotStarter


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("settings.ini")
    BotStarter(config['Bot']['token'], int(config['Chat']['kick_min'])).handle()
