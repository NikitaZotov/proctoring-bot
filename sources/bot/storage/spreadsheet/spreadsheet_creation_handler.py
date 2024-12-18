from typing import Dict, List, Optional

from sources.bot.storage.spreadsheet.base_spreadsheet_handler import BaseSpreadsheetHandler
from sources.bot.storage.spreadsheet.spreadsheet_handler import SpreadsheetHandler


class SpreadsheetCreationHandler(BaseSpreadsheetHandler):
    def __init__(self, spreadsheet_id: str, file_name: str):
        """
        Initializes the spreadsheet creation handler.

        :param spreadsheet_id: The ID of the spreadsheet.
        :param file_name: The name of the spreadsheet file.
        """
        self._sheet_data: Optional[Dict[str, List[str]]] = None
        self._sheet_title: Optional[str] = None
        self._spreadsheet_id = None
        self._spreadsheet_viewing_mode: str = "reader"
        self._handler = SpreadsheetHandler(file_name, spreadsheet_id)

    def set_attributes(self, sheet_data: Dict[str, List[str]], viewing_mode: str) -> None:
        """
        Sets the attributes required for spreadsheet creation.

        :param sheet_data: Spreadsheet data in a dictionary format where the key is the sheet title,
                           and the value is a list of rows to be added.
        :param viewing_mode: The access mode for the spreadsheet (e.g., "reader" or "editor").
        """
        self._sheet_data = sheet_data
        self._sheet_title = list(self._sheet_data.keys())[0]
        self._spreadsheet_viewing_mode = viewing_mode

    def create_spreadsheet(self, spreadsheet_title: str = None) -> str:
        """
        Creates a spreadsheet with the specified title and returns its ID.

        :param spreadsheet_title: The title of the spreadsheet.
        :return: The ID of the created spreadsheet.
        """
        self._spreadsheet_id = self._handler.create_spreadsheet(spreadsheet_title, self._sheet_title)
        if self._spreadsheet_viewing_mode != "reader":
            self._handler._get_permissions(self._spreadsheet_viewing_mode)
        self._handler.add_row(self._sheet_title, self._sheet_data.get(self._sheet_title)[0])
        return self._spreadsheet_id