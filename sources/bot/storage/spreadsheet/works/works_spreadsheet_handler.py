from ....exceptions import InvalidSpreadsheetAttributeException
from ..spreadsheet_handler import SpreadsheetHandler
from .base_works_spreadsheet_handler import BaseWorksSpreadsheetHandler


class WorksSpreadsheetHandler(BaseWorksSpreadsheetHandler):
    def __init__(self, spreadsheet_id: str, file_name: str):
        self._attributes = {
            "works": ["username", "ФИО", "Группа", "Подгруппа", "Лабораторная работа"],
        }
        self._handler = SpreadsheetHandler(file_name, spreadsheet_id)
        self._works_sheet_title = list(self._attributes.keys())[0]

    def create_spreadsheet(self, spreadsheet_title="Информация о лабораторных работах") -> None:
        self._handler.create_spreadsheet(spreadsheet_title)
        self._handler.add_row(spreadsheet_title, self._attributes.get("works"))

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
            self._handler.add_row(self._works_sheet_title, [username, name, group, subgroup, work])

    def remove_student(self, username: str) -> bool:
        return self._handler.remove_row(self._works_sheet_title, username)

    def accept_storage(self, storage):
        storage.visit_works_handler(self)

    def get_student_lab_count(self) -> dict:
        """
        Counts the number of valid lab works for each student.

        A lab work is considered valid if it has a non-empty grade and the grade is >= 4.

        :return: Dictionary mapping usernames to the count of valid lab works.
        :rtype: dict
        """
        try:
            data = self._handler.get_sheet_values(self._works_sheet_title, "A2", "F1000")  # Обновлено на "F1000"
            rows = data.get("valueRanges", [{}])[0].get("values", [])
            lab_count = {}

            for row in rows:
                if len(row) >= 6:  # Убедиться, что в строке есть все необходимые столбцы
                    username = row[0]
                    grade = row[5]  # Столбец с оценкой ("Оценка")

                    # Проверка: оценка должна быть числом >= 4
                    try:
                        grade = int(grade)
                        if grade >= 4:
                            if username in lab_count:
                                lab_count[username] += 1
                            else:
                                lab_count[username] = 1
                    except ValueError:
                        # Если оценка не является числом, пропускаем
                        continue

            return lab_count
        except Exception as e:
            raise InvalidSpreadsheetAttributeException(f"Failed to count lab works: {e}")

