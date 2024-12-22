from ..util.spreadsheet_config import SpreadsheetConfig
from ....exceptions import InvalidSpreadsheetAttributeException
from ..spreadsheet_handler import SpreadsheetHandler
from .base_works_spreadsheet_handler import BaseWorksSpreadsheetHandler


class WorksSpreadsheetHandler(BaseWorksSpreadsheetHandler):
    def __init__(self, spreadsheet_id: str, file_name: str, config_class=None):
        self._attributes = {
            "works": ["username", "ФИО", "Группа", "Подгруппа", "Лабораторная работа"],
        }
        self._config: SpreadsheetConfig = config_class
        self._handler = SpreadsheetHandler(file_name, spreadsheet_id)
        self._works_sheet_title = list(self._attributes.keys())[0]

    def handler(self):
        spreadsheet_id: str = self._config.works_id
        file_name: str = self._config.works_token
        return SpreadsheetHandler(file_name, spreadsheet_id)

    def create_spreadsheet(self, spreadsheet_title="Информация о лабораторных работах") -> None:
        handler = self.handler()
        handler.create_spreadsheet(spreadsheet_title)
        handler.add_row(spreadsheet_title, self._attributes.get("works"))

    def add_student_work(self, username: str, works_data: str, **kwargs) -> None:
        name = kwargs.get("name")
        group = kwargs.get("group")
        subgroup = kwargs.get("subgroup")
        work = works_data

        if not name:
            raise InvalidSpreadsheetAttributeException("Invalid name value")
        elif not group:
            raise InvalidSpreadsheetAttributeException("Invalid group value")
        elif not subgroup:
            raise InvalidSpreadsheetAttributeException("Invalid subgroup value")
        elif not work:
            raise InvalidSpreadsheetAttributeException("Invalid work value")
        else:
            self.handler().add_row(self._works_sheet_title, [username, name, group, work])

    def remove_student(self, username: str) -> bool:
        return self.handler().remove_row(self._works_sheet_title, username)

    def accept_storage(self, storage):
        storage.visit_works_handler(self)
