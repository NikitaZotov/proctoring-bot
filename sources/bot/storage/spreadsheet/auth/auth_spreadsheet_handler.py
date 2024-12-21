"""
Students authorization spreadsheet handler implementation module.
"""
from typing import List

from ....exceptions import InvalidSpreadsheetAttributeException
from ...base_spreadsheet_storage import BaseSpreadsheetStorage
from ..spreadsheet_handler import SpreadsheetHandler
from ..auth.base_auth_spreadsheet_handler import BaseAuthSpreadsheetHandler


class AuthSpreadsheetHandler(BaseAuthSpreadsheetHandler):
    """
    Students authorization spreadsheet handler class implementation.
    """

    def __init__(self, spreadsheet_id: str, file_name: str):
        self._attributes = {
            "Студенты": ["username", "ФИО", "Группа", "Подгруппа", "Допуск"],
            "Преподаватели": ["username", "ФИО"],
        }
        self._handler = SpreadsheetHandler(file_name, spreadsheet_id)
        self._student_sheet_title = list(self._attributes.keys())[0]
        self._teacher_sheet_title = list(self._attributes.keys())[1]

    def create_spreadsheet(self, spreadsheet_title="Информация о людях"):
        self._handler.create_spreadsheet(spreadsheet_title, self._student_sheet_title)
        self._handler.add_row(self._student_sheet_title, self._attributes.get(self._student_sheet_title))
        self._handler.create_sheet(self._teacher_sheet_title)
        self._handler.add_row(self._teacher_sheet_title, self._attributes.get(self._teacher_sheet_title))

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
            self._handler.add_row(self._student_sheet_title, [username, name, group, subgroup])

    def remove_student(self, username: str) -> bool:
        return self._handler.remove_row(self._student_sheet_title, username)

    def get_student_usernames(self) -> List[str]:
        return self._handler.get_first_column_values(self._student_sheet_title)

    def get_student_by_username(self, username: str) -> dict:
        student = {}
        data = self._handler.get_row_by_first_element(self._student_sheet_title, username)
        name = data.get("ФИО")
        group = data.get("Группа")
        subgroup = data.get("Подгруппа")

        if name and group and subgroup:
            student.update(name=name, group=group, subgroup=subgroup)

        return student

    def update_student_name(self, username: str, new_name: str) -> bool:
        if not new_name.strip():
            raise InvalidSpreadsheetAttributeException("Invalid name value.")
        row = self._handler.get_row_by_first_element(self._student_sheet_title, username)
        if not row:
            raise InvalidSpreadsheetAttributeException(f"Student with username '{username}' was not found!")

        attributes = self._handler._get_sheet_attributes(self._student_sheet_title)
        name_index = attributes.index("ФИО")

        row_number = self._handler.get_first_column_values(self._student_sheet_title).index([username]) + 2
        row_values = list(row.values())
        row_values[name_index] = new_name

        try:
            self._handler._update_spreadsheet_row(self._student_sheet_title, row_number, row_values)
            return True
        except Exception as e:
            raise InvalidSpreadsheetAttributeException(f"Failed to update student row: {e}")

    def get_service(self):
        """
        Returns the service object to interact with Google Sheets API.
        """
        return self._handler._service

    def batch_update_admission_status(self, admissions: dict) -> None:
        """
        Batch updates the admission statuses for multiple students.

        :param admissions: A dictionary where keys are usernames and values are statuses ("Допуск" or "Недопуск")
        :type admissions: dict
        """
        try:
            rows = self._handler.get_first_column_values(self._student_sheet_title)
            attributes = self._handler._get_sheet_attributes(self._student_sheet_title)
            admission_index = attributes.index("Допуск")

            updates = []

            for i, row in enumerate(rows, start=2): 
                username = row[0]
                if username in admissions:
                    updates.append({
                        "range": f"{self._student_sheet_title}!{chr(65 + admission_index)}{i}",
                        "values": [[admissions[username]]]
                    })
            service = self.get_service()

            if updates:
                service.spreadsheets().values().batchUpdate(
                    spreadsheetId=self._handler._spreadsheet_id,
                    body={
                        "valueInputOption": "USER_ENTERED",
                        "data": updates
                    }
                ).execute()

        except Exception as e:
            raise InvalidSpreadsheetAttributeException(f"Failed to batch update admission statuses: {e}")

    def add_teacher(self, username: str, **kwargs) -> None:
        name = kwargs.get("name")

        if not name:
            raise InvalidSpreadsheetAttributeException("Invalid name value")
        else:
            self._handler.add_row(self._teacher_sheet_title, [username, name])

    def remove_teacher(self, username: str) -> bool:
        return self._handler.remove_row(self._teacher_sheet_title, username)

    def get_teacher_usernames(self) -> List[str]:
        return self._handler.get_first_column_values(self._teacher_sheet_title)

    def get_teacher_by_username(self, username: str) -> dict:
        teacher = {}
        data = self._handler.get_row_by_first_element(self._teacher_sheet_title, username)
        name = data.get("ФИО")

        if name:
            teacher.update(name=name)

        return teacher

    def accept_storage(self, storage: BaseSpreadsheetStorage):
        storage.visit_auth_handler(self)
