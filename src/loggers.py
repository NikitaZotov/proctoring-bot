"""
"""

import logging

from constants import log_formats


class LogInstaller:
    @staticmethod
    def add_format(other: dict):
        log_formats.update(other)

    @staticmethod
    def get_logger(package_name: str, format_name: str, level: int) -> logging.Logger:
        logger = logging.getLogger(package_name)
        logging.basicConfig(
            level=level,
            format=log_formats.get(format_name),
        )
        return logger

    @staticmethod
    def get_default_logger(package_name: str, level: int) -> logging.Logger:
        return LogInstaller.get_logger(package_name, 'default', level)

