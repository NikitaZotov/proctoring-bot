"""
Students deadline spreadsheet handler implementation module.
"""
from typing import List

from sources.bot.exceptions import InvalidSpreadsheetAttributeException
from sources.bot.storage.base_spreadsheet_storage import BaseSpreadsheetStorage
from sources.bot.storage.spreadsheet.spreadsheet_handler import SpreadsheetHandler
from sources.bot.storage.spreadsheet.deadline.base_deadline_spreadsheet_handler import BaseDeadlineSpreadsheetHandler
from sources.bot.loggers import LogInstaller


class DeadlineSpreadsheetHandler(BaseDeadlineSpreadsheetHandler):
    """
    Students deadline spreadsheet handler class implementation.
    """

    def __init__(self, spreadsheet_id: str, file_name: str):
        self._logger = LogInstaller.get_default_logger(__name__, LogInstaller.DEBUG)
        self._attributes = {
            "Labs": ["Название дисциплины", "Название лабораторной", "Дедлайн", "Описание лабораторной"]}
        self._handler = SpreadsheetHandler(file_name, spreadsheet_id)
        self._labs_sheet_title = list(self._attributes.keys())[0]

    def create_spreadsheet(self, spreadsheet_title="Laboratory works"):
        self._handler.create_spreadsheet(spreadsheet_title, self._labs_sheet_title)
        self._handler.add_row(self._labs_sheet_title, self._attributes.get(self._labs_sheet_title))
        self._logger.debug(f"Method create_spreadsheet({self._labs_sheet_title})")

    def add_deadline(self, **kwargs):
        discipline_name = kwargs.get("discipline_name")
        lab_name = kwargs.get("lab_name")
        deadline = kwargs.get("deadline")
        description = kwargs.get("description", "")

        if not all([discipline_name, lab_name, deadline]):
            raise InvalidSpreadsheetAttributeException("Missing required deadline information")

        self._handler.add_row(self._labs_sheet_title, [
            discipline_name,
            lab_name,
            deadline,
            description
        ])
        self._logger.debug(f"Added deadline for {lab_name}")

    def get_deadline(self, discipline_name: str = None, lab_name: str = None) -> List[dict]:
        results = []
        data = self._handler.get_sheet_values(
            self._labs_sheet_title,
            "A2",
            "F1000"
        )

        if data["valueRanges"][0].get("values"):
            sheet_values = data["valueRanges"][0]["values"]

            for row in sheet_values:
                if len(row) < 4:
                    continue

                if (discipline_name and row[0] != discipline_name) or \
                        (lab_name and row[1] != lab_name):
                    continue

                deadline_info = {
                    "discipline_name": row[0],
                    "lab_name": row[1],
                    "deadline": row[2],
                    "description": row[3] if len(row) > 3 else ""
                }
                results.append(deadline_info)

        return results

    def get_deadlines(self) -> List[dict]:
        deadlines = self.get_deadline()

        return deadlines

    def accept_storage(self, storage: BaseSpreadsheetStorage):
        storage.visit_deadline_handler(self)
