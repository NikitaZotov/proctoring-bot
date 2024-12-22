from sources.bot.storage.spreadsheet.util.spreadsheet_config import SpreadsheetConfig


class SpreadsheetConfigurator:
    @staticmethod
    def configure_spreadsheet(generated_ini, generated_json_dir):
        SpreadsheetConfig.ini_path = generated_ini
        SpreadsheetConfig.json_dir_path = generated_json_dir
        SpreadsheetConfig.load_from_file()
