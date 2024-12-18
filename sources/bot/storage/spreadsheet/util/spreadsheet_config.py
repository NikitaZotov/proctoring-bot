import os
from dataclasses import dataclass
from configparser import ConfigParser
from typing import Optional


@dataclass
class SpreadsheetConfig:
    auth_id: Optional[str] = None
    auth_token: Optional[str] = None
    works_id: Optional[str] = None
    works_token: Optional[str] = None
    tests_id: Optional[str] = None
    tests_token: Optional[str] = None

    ini_path: Optional[str] = None
    json_dir_path: Optional[str] = None

    @classmethod
    def load_from_file(cls):
        if not cls.ini_path or not os.path.exists(cls.ini_path):
            return

        config = ConfigParser()
        config.read(cls.ini_path)

        if "Spreadsheet" not in config:
            return

        spreadsheet_section = config["Spreadsheet"]
        if spreadsheet_section:
            cls.auth_id = spreadsheet_section.get("auth_id")
            cls.auth_token = spreadsheet_section.get("auth_token")
            cls.works_id = spreadsheet_section.get("works_id")
            cls.works_token = spreadsheet_section.get("works_token")
            cls.tests_id = spreadsheet_section.get("tests_id")
            cls.tests_token = spreadsheet_section.get("tests_token")

    @classmethod
    def save_to_file(cls, file_path: str):
        config = ConfigParser()
        config["Spreadsheet"] = {
            "auth_id": cls.auth_id or "",
            "auth_token": cls.auth_token or "",
            "works_id": cls.works_id or "",
            "works_token": cls.works_token or "",
            "tests_id": cls.tests_id or "",
            "tests_token": cls.tests_token or "",
        }

        with open(file_path, "w") as configfile:
            config.write(configfile)

    @classmethod
    def save(cls):
        cls.save_to_file(cls.ini_path)

    @classmethod
    def set_value_and_save(cls, key: str, value: str):
        if hasattr(cls, key):
            setattr(cls, key, value)
        else:
            raise KeyError(f"Invalid key: {key}")
        cls.save()

    @classmethod
    def set_value(cls, key: str, value: str):
        if hasattr(cls, key):
            if not getattr(cls, key, None):
                setattr(cls, key, value)
        else:
            raise KeyError(f"Invalid key: {key}")
