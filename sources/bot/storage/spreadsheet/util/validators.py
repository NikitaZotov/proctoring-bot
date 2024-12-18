import re


def validate_and_extract_id(sheet_url):
    pattern = r"https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]{44})"
    match = re.search(pattern, sheet_url)
    if match:
        return match.group(1)
    return None


def validate_json_filename(filename):
    if not filename.endswith('.json'):
        return False
    return True
