"""
Students authorization spreadsheet handler interface module.
"""
from abc import ABCMeta, abstractmethod
from typing import List

from sources.bot.storage.spreadsheet.base_spreadsheet_handler import BaseSpreadsheetHandler


class BaseDeadlineSpreadsheetHandler(BaseSpreadsheetHandler):
    """
    Students authorization spreadsheet handler interface.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def add_deadline(self, deadline: str, **kwargs):
        """
        Adds student data in spreadsheet.

        :param deadline: Deadline for student
        :type deadline: :obj:`str`

        :param kwargs: Deadline data
        :type kwargs: :obj:`dict`
        """
        raise NotImplementedError

    @abstractmethod
    def get_deadlines(self) -> List[str]:
        """
        Gets all student usernames from spreadsheet.

        Note: If such students don't exist then [] will be returned.

        :return: Returns usernames list.
        :rtype: :obj:`List[str]`
        """
        raise NotImplementedError

    @abstractmethod
    def get_deadline(self, deadline: str) -> dict:
        """
        Gets student with fields from spreadsheet by his username.

        Note: If such student doesn't exist then {} will be returned.

        :param deadline: Student username
        :type deadline: :obj:`str`

        :return: Returns student data.
        :rtype: :obj:`dict`
        """
        raise NotImplementedError
