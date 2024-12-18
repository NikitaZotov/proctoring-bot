"""
Students authorization spreadsheet handler implementation module.
"""
from typing import List

from ..util.spreadsheet_config import SpreadsheetConfig
from ....exceptions import InvalidSpreadsheetAttributeException
from ...base_spreadsheet_storage import BaseSpreadsheetStorage
from ..spreadsheet_handler import SpreadsheetHandler
from ..auth.base_auth_spreadsheet_handler import BaseAuthSpreadsheetHandler


class AuthSpreadsheetHandler(BaseAuthSpreadsheetHandler):
    """
    Students authorization spreadsheet handler class implementation.
    """

    def __init__(self, spreadsheet_id: str, file_name: str, config_class=None):
        self._attributes = {
            "Студенты": ["username", "ФИО", "Группа", "Подгруппа"],
            "Преподаватели": ["username", "ФИО"],
        }
        self._config: SpreadsheetConfig = config_class
        self._handler = SpreadsheetHandler(file_name, spreadsheet_id)
        self._student_sheet_title = list(self._attributes.keys())[0]
        self._teacher_sheet_title = list(self._attributes.keys())[1]

    def handler(self):
        spreadsheet_id: str = self._config.auth_id
        file_name: str = self._config.auth_token
        return SpreadsheetHandler(file_name, spreadsheet_id)

    def create_spreadsheet(self, spreadsheet_title="Информация о людях"):
        handler = self.handler()
        handler.create_spreadsheet(spreadsheet_title, self._student_sheet_title)
        handler.add_row(self._student_sheet_title, self._attributes.get(self._student_sheet_title))
        handler.create_sheet(self._teacher_sheet_title)
        handler.add_row(self._teacher_sheet_title, self._attributes.get(self._teacher_sheet_title))

    def add_student(self, username: str, **kwargs):
        name = kwargs.get("name")
        group = kwargs.get("group")
        subgroup = kwargs.get("subgroup")

        if not name:
            raise InvalidSpreadsheetAttributeException("Invalid name value")
        elif not group:
            raise InvalidSpreadsheetAttributeException("Invalid group value")
        elif not subgroup:
            raise InvalidSpreadsheetAttributeException("Invalid subgroup value")
        else:
            self.handler().add_row(self._student_sheet_title, [username, name, group, subgroup])

    def remove_student(self, username: str) -> bool:
        return self.handler().remove_row(self._student_sheet_title, username)

    def get_student_usernames(self) -> List[str]:
        return self.handler().get_first_column_values(self._student_sheet_title)

    def get_student_by_username(self, username: str) -> dict:
        student = {}
        data = self.handler().get_row_by_first_element(self._student_sheet_title, username)
        name = data.get("ФИО")
        group = data.get("Группа")
        subgroup = data.get("Подгруппа")

        if name and group and subgroup:
            student.update(name=name, group=group, subgroup=subgroup)

        return student

    def add_teacher(self, username: str, **kwargs) -> None:
        name = kwargs.get("name")

        if not name:
            raise InvalidSpreadsheetAttributeException("Invalid name value")
        else:
            self.handler().add_row(self._teacher_sheet_title, [username, name])

    def remove_teacher(self, username: str) -> bool:
        return self.handler().remove_row(self._teacher_sheet_title, username)

    def get_teacher_usernames(self) -> List[str]:
        return self.handler().get_first_column_values(self._teacher_sheet_title)

    def get_teacher_by_username(self, username: str) -> dict:
        teacher = {}
        data = self.handler().get_row_by_first_element(self._teacher_sheet_title, username)
        name = data.get("ФИО")

        if name:
            teacher.update(name=name)

        return teacher

    def accept_storage(self, storage: BaseSpreadsheetStorage):
        storage.visit_auth_handler(self)
