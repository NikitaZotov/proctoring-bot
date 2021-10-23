import configparser

from proctoring_bot import ProctoringBot


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("settings.ini")
    ProctoringBot(config['Bot']['token'], int(config['Chat']['kick_min']), config['Spreadsheet']['id']).start()

