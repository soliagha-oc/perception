# from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import gspread
# from globals import Globals
from flask import Flask
import os
from google.auth.transport.requests import Request

# App config
app = Flask(__name__)
app.config.from_object('config.Config')
PROCESS_LOG = app.config.get('PROCESS_LOG')
BASE_FOLDER = app.config.get('BASE_FOLDER')
REPORTS_FOLDER = app.config.get('REPORTS_FOLDER')
GMAIL_USER = app.config.get('GMAIL_USER')
GMAIL_PASSWORD = app.config.get('GMAIL_PASSWORD')
GOOGLE_FOLDER_ID = app.config.get('GOOGLE_FOLDER_ID')
GOOGLE_TEMPLATE_ID = app.config['GOOGLE_TEMPLATE_ID']
SENT_FROM = app.config.get('SENT_FROM')

# If modifying these scopes, delete the file token.pickle.
SCOPES_SHEETS = ['https://www.googleapis.com/auth/spreadsheets']
SCOPES_DRIVE = ['https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1C1ZWvl5ZKwkgkJ8aO5Jkl10tSDhT_sJQFvJ1Hf7SvlI'
RANGE_NAME = 'Sheet1!A:A'

class GDRIVE:
    def __init__(self, folder_name, report_type, data):
        self.name = 'PERCEPTION Evaluation: ' + folder_name.replace('_', ' ')
        self.report_path = os.path.join(REPORTS_FOLDER, folder_name)
        self.report_type = report_type
        self.folder_name = folder_name
        self.data = data
        self.main()

    def main(self):
        # Set Google template and folder ID


        drive = build('drive', 'v3', credentials=self.get_creds(SCOPES_DRIVE))
        gs = gspread.authorize(self.get_creds(SCOPES_SHEETS))
        sheet_id = None
        log_gdrive = os.path.join(self.report_path, 'logs', '_gdrive_log.txt')
        if os.path.exists(log_gdrive):
            with open(log_gdrive) as file:
                sheet_id = file.readline()
        else:
            sheet_id = gs.copy(GOOGLE_TEMPLATE_ID, title=self.name, copy_permissions=True).id
            file = drive.files().get(fileId=sheet_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))
            # Move the file to the new folder
            file = drive.files().update(fileId=sheet_id,
                                        addParents=GOOGLE_FOLDER_ID,
                                        removeParents=previous_parents,
                                        fields='id, parents').execute()

            with open(log_gdrive, mode='a+', encoding='utf8') as file:
                file.write(sheet_id)

        # CREATE FROM TEMPLATE
        sheet = gs.open_by_key(sheet_id)
        worksheet = None
        worksheets = sheet.worksheets()
        sheet_range = ''

        if self.report_type == 'dash':
            try:
                ws_index = 0
                for ws in worksheets:
                    if ws.title == 'DASHBOARD':
                        sheet.del_worksheet(ws)
                ts = gs.open('REPORT TEMPLATE').get_worksheet(ws_index).copy_to(spreadsheet_id=sheet_id)
                worksheets = sheet.worksheets()
                my_sheet = worksheets.__getitem__(worksheets.__len__() - 1)
                my_sheet.update_title('DASHBOARD')
                my_sheet.update_index(ws_index)
                worksheet = sheet.get_worksheet(ws_index)
                sheet_range = 'DASHBOARD!A4:Z1000'
            except Exception as e:
                print(str(e))
        if self.report_type == 'axe_c_summary':
            ws_index = 2
            for ws in worksheets:
                if ws.title == 'AXE':
                    sheet.del_worksheet(ws)
            gs.open('REPORT TEMPLATE').get_worksheet(ws_index).copy_to(spreadsheet_id=sheet_id)
            worksheets = sheet.worksheets()
            my_sheet = worksheets.__getitem__(worksheets.__len__() - 1)
            my_sheet.update_title('AXE')
            my_sheet.update_index(ws_index)
            worksheet = sheet.get_worksheet(ws_index)
            sheet_range = 'AXE!A10:Z1000'
        if self.report_type == 'lighthouse':
            ws_index = 3
            for ws in worksheets:
                if ws.title == 'LIGHTHOUSE':
                    sheet.del_worksheet(ws)
            gs.open('REPORT TEMPLATE').get_worksheet(ws_index).copy_to(spreadsheet_id=sheet_id)
            worksheets = sheet.worksheets()
            my_sheet = worksheets.__getitem__(worksheets.__len__() - 1)
            my_sheet.update_title('LIGHTHOUSE')
            my_sheet.update_index(ws_index)
            worksheet = sheet.get_worksheet(ws_index)
            sheet_range = 'LIGHTHOUSE!A10:Z1000'
        if self.report_type == 'pdf_internal':
            ws_index = 4
            for ws in worksheets:
                if ws.title == 'PDF INTERNAL':
                    sheet.del_worksheet(ws)
            gs.open('REPORT TEMPLATE').get_worksheet(ws_index).copy_to(spreadsheet_id=sheet_id)
            worksheets = sheet.worksheets()
            my_sheet = worksheets.__getitem__(worksheets.__len__() - 1)
            my_sheet.update_title('PDF INTERNAL')
            my_sheet.update_index(ws_index)
            worksheet = sheet.get_worksheet(ws_index)
            sheet_range = worksheet.title
        if self.report_type == 'pdf_external':
            ws_index = 5
            for ws in worksheets:
                if ws.title == 'PDF EXTERNAL':
                    sheet.del_worksheet(ws)
            worksheets = sheet.worksheets()
            my_sheet = worksheets.__getitem__(worksheets.__len__() - 1)
            my_sheet.update_title('PDF EXTERNAL')
            my_sheet.update_index(ws_index)
            worksheet = sheet.get_worksheet(ws_index)
            sheet_range = worksheet.title

        if worksheet:
            value_input_option = 'USER_ENTERED'
            # values = [self.data]
            values = []
            for row in self.data:
                value = ''
                if self.report_type.find('pdf') == 0:
                    value = [row.errors, row.title.replace('`', '').replace('"', ''),
                             row.description.replace('`', '').replace('"', '')]
                    values.append(value)
                elif self.report_type == 'dash':
                    value = [row.metric, row.url_count, row.percentage, row.urls_total,
                             row.description.replace('`', '').replace('"', '')]
                    values.append(value)
                elif self.report_type == 'axe_c':
                    value = [row.url, row.error_count, row.error_description.replace('`', '').replace('"', '')]
                    values.append(value)
                else:
                    value = [row.error_count, row.error.replace('`', '').replace('"', ''),
                             row.error_description.replace('`', '').replace('"', '')]
                    values.append(value)
            body = {'values': values}
            sheets = build('sheets', 'v4', credentials=self.get_creds(SCOPES_SHEETS))
            # clear sheet
            sheets.spreadsheets().values().clear(
                spreadsheetId=sheet.id, range=sheet_range, body={}).execute()

            result = sheets.spreadsheets().values().update(
                spreadsheetId=sheet.id, range=sheet_range,
                valueInputOption=value_input_option, body=body).execute()

            # Read CSV file contents
            print('{0} cells updated.'.format(result.get('updatedCells')))
            try:
                filepath = os.path.join(self.report_path, 'AXE', 'CHROME', 'AXE_CHROME_SUMMARY.csv')
                self.paste_csv(filepath, sheet, 'AXE DATA (CHROME)!A1')
            except Exception as e:
                print(str(e))
            try:
                filepath = os.path.join(self.report_path, 'AXE', 'FIREFOX', 'AXE_FIREFOX_SUMMARY.csv')
                self.paste_csv(filepath, sheet, 'AXE DATA (FIREFOX)!A1')
            except Exception as e:
                print(str(e))
            try:
                filepath = os.path.join(self.report_path, 'LIGHTHOUSE', 'LIGHTHOUSE_REPORT.csv')
                self.paste_csv(filepath, sheet, 'LIGHTHOUSE DATA!A1')
            except Exception as e:
                print(str(e))
            try:
                filepath = os.path.join(self.report_path, 'PDF', 'internal_pdf_a.csv')
                self.paste_csv(filepath, sheet, 'PDF INTERNAL DATA!A1')
            except Exception as e:
                print(str(e))
            try:
                filepath = os.path.join(self.report_path, 'PDF', 'external_pdf_a.csv')
                self.paste_csv(filepath, sheet, 'PDF EXTERNAL DATA!A1')
            except Exception as e:
                print(str(e))

    def paste_csv(self, csvfile, sheet, cell):
        import gspread as gs
        if '!' in cell:
            (tabName, cell) = cell.split('!')
            wks = sheet.worksheet(tabName)
        else:
            wks = sheet.sheet1
        (firstRow, firstColumn) = gs.utils.a1_to_rowcol(cell)

        with open(csvfile, 'r') as f:
            csvContents = f.read()
        body = {
            'requests': [{
                'pasteData': {
                    "coordinate": {
                        "sheetId": wks.id,
                        "rowIndex": firstRow - 1,
                        "columnIndex": firstColumn - 1,
                    },
                    "data": csvContents,
                    "type": 'PASTE_NORMAL',
                    "delimiter": ',',
                }
            }]
        }
        return sheet.batch_update(body)

    def get_creds(self, SCOPE):
        creds = None
        json = os.path.join(BASE_FOLDER, 'credentials.json')
        path = 'token.pickle'
        if os.path.exists(path):
            with open(path, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(json, SCOPE)
                creds = flow.run_local_server(port=0)
            with open(path, 'wb') as token:
                pickle.dump(creds, token)

        return creds


def hold(self):

    # CREATE FOLDER
    drive = build('drive', 'v3', credentials=self.get_creds(SCOPES_DRIVE))
    file_metadata = {
        'name': self.folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.files().create(body=file_metadata, fields='id').execute()
    # print('Folder ID: %s' % folder.get('id'))

    # CREATE SPREADSHEET
    file_metadata = {
        'name': self.folder_name,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [folder.get('id')]
    }
    spreadsheet = drive.files().create(body=file_metadata, fields='id').execute()

    value_input_option = 'USER_ENTERED'
    # values = [self.data]
    values = []
    for row in self.data:
        value = ''
        value = [row.error_count, row.error.replace('`', '').replace('"', ''),
                 row.error_description.replace('`', '').replace('"', '')]
        values.append(value)
    body = {'values': values}
    sheets = build('sheets', 'v4', credentials=self.get_creds(SCOPES_SHEETS))
    result = sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet["id"], range='Sheet1',
        valueInputOption=value_input_option, body=body).execute()

    print('{0} cells updated.'.format(result.get('updatedCells')))
