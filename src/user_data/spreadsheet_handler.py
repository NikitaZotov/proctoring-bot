import configparser

import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials


class SpreadSheetHandler:
    __credentials_file = 'token.json'

    __credentials = ServiceAccountCredentials.from_json_keyfile_name(__credentials_file,
                                                                     ['https://www.googleapis.com/auth/spreadsheets',
                                                                      'https://www.googleapis.com/auth/drive'])
    __http_auth = __credentials.authorize(httplib2.Http())
    __service = apiclient.discovery.build('sheets', 'v4', http=__http_auth)

    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id

    def __create_student_sheet(self) -> None:
        self.__service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=
            {
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": "Студенты",
                                "gridProperties": {
                                    "rowCount": 200,
                                    "columnCount": 8
                                }
                            }
                        }
                    }
                ]
            }).execute()

        self.__service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
            "valueInputOption": "USER_ENTERED",
            "calle2": [
                {"range": "Студенты!A1:D1",
                 "majorDimension": "ROWS",
                 "values": [["username", "ФИО", "Группа", "Подруппа"]]},
            ]
        }).execute()

    def create_spreadsheet(self) -> None:
        spreadsheet = self.__service.spreadsheets().create(body={
            'properties': {'title': 'Информация о людях', 'locale': 'ru_RU'},
            'sheets': [{'properties': {'sheetType': 'GRID',
                                       'sheetId': 0,
                                       'title': 'Преподаватели',
                                       'gridProperties': {'rowCount': 100, 'columnCount': 8}}}]
        }).execute()

        self.spreadsheet_id = spreadsheet['spreadsheetId']

        self.__service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
            "valueInputOption": "USER_ENTERED",
            "calle2": [
                {"range": "Преподаватели!A1:B1",
                 "majorDimension": "ROWS",
                 "values": [["username", "ФИО"]]},
            ]
        }).execute()

        self.__create_student_sheet()

        print('https://docs.google.com/spreadsheets/d/' + self.spreadsheet_id + '/edit#gid=0')

        self.__get_permissions()

    def __get_permissions(self) -> None:
        drive_service = apiclient.discovery.build('drive', 'v3', http=self.__http_auth)

        drive_service.permissions().create(
            fileId=self.spreadsheet_id,
            body={'type': 'user', 'role': 'writer', 'emailAddress': 'orlovmassimo@gmail.com'},
            # Чтобы редактировать таблицу вручную
            # body={'type': 'anyone', 'role': 'reader'},
            fields='id'
        ).execute()

    def add_student(self, username: str, name: str, group: str, subgroup: str) -> None:
        ranges = ["Студенты!A1:A100"]

        results = self.__service.spreadsheets().values().batchGet(spreadsheetId=self.spreadsheet_id,
                                                                  ranges=ranges,
                                                                  valueRenderOption='FORMATTED_VALUE',
                                                                  dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']

        row_number = len(sheet_values) + 1

        self.__service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
            "valueInputOption": "USER_ENTERED",
            "calle2": [
                {"range": f"Студенты!A{row_number}:D{row_number}",
                 "majorDimension": "ROWS",
                 "values": [[username, name, group, subgroup]]},
            ]
        }).execute()

    def delete_student(self, username: str) -> None:
        ranges = ["Студенты!A2:A100"]

        results = self.__service.spreadsheets().values().batchGet(spreadsheetId=self.spreadsheet_id,
                                                                  ranges=ranges,
                                                                  valueRenderOption='FORMATTED_VALUE',
                                                                  dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']

        row_number = sheet_values.index([username]) + 2
        self.__service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
            "valueInputOption": "USER_ENTERED",
            "calle2": [
                {"range": f"Студенты!A{row_number}:D{row_number}",
                 "majorDimension": "ROWS",
                 "values": [['', '', '', '']]},
            ]
        }).execute()

    def get_student_usernames(self) -> list:
        ranges = ["Студенты!A2:A100"]

        results = self.__service.spreadsheets().values().batchGet(spreadsheetId=self.spreadsheet_id,
                                                                  ranges=ranges,
                                                                  valueRenderOption='FORMATTED_VALUE',
                                                                  dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        return sheet_values

    def get_student_by_username(self, username: str) -> dict:
        ranges = ["Студенты!A2:D100"]

        results = self.__service.spreadsheets().values().batchGet(spreadsheetId=self.spreadsheet_id,
                                                                  ranges=ranges,
                                                                  valueRenderOption='FORMATTED_VALUE',
                                                                  dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']

        user = []
        for user_row in sheet_values:
            for user_name in user_row:
                if user_name == username:
                    user = user_row

        return {username: user}


if __name__ == '__main__':
    # config = configparser.ConfigParser()
    # config.read("settings.ini")
    # s_id = config['Spreadsheet']['spreadsheet_id']
    ssh = SpreadSheetHandler('1Hizb45BFtKPS5Rnmx8Eb5KvXVy0Pn_tW4kgyAD3rxfw')
    ssh.add_student('Mksm', 'Maksim Orlov Konst', '921701', '1')
    print(ssh.get_student_by_username('Zotoz'))
    print(ssh.get_student_usernames())
