import json
import os
import sys

from typing import List


class JsonTestFileUtil:
    @staticmethod
    def save_test(test_name: str, test: List[dict]) -> None:
        if not test_name == "":
            current_path = os.path.dirname(sys.argv[0])  # needs to be configured in config.ini
            path = f"{current_path}\\surveys"
            os.makedirs(path, exist_ok=True)
            with open(f"surveys/{test_name}.json", "w", encoding="utf-8") as f:
                json.dump(test, f, ensure_ascii=False, indent=4)

    @staticmethod
    def get_test_from_file(survey_sheet_name: str):
        with open(f"surveys/{survey_sheet_name}.json", encoding="utf-8") as json_file:
            return json.load(json_file)
