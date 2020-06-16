from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import gspread
from globals import Globals
import os
from oauth2client.service_account import ServiceAccountCredentials

'''import oauth2client.file as file
from oauth2client import client
from oauth2client import file
from oauth2client import tools'''
from google.auth.transport.requests import Request
from flask import Flask, render_template, flash, request

# If modifying these scopes, delete the file token.pickle.
SCOPES_SHEETS = ['https://www.googleapis.com/auth/spreadsheets']
SCOPES_DRIVE = ['https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1C1ZWvl5ZKwkgkJ8aO5Jkl10tSDhT_sJQFvJ1Hf7SvlI'
RANGE_NAME = 'Sheet1!A:A'


class GDRIVE:
    def __init__(self, folder_name, report_type, data):
        self.name = 'PERCEPTION Evaluation: ' + folder_name.replace('_', ' ')
        self.report_path = Globals.gbl_report_folder + folder_name + '\\'
        self.report_type = report_type
        self.folder_name = folder_name
        self.data = data
        self.main()

    def main(self):
        # Set Google template and folder ID
        template_id = Globals.template_id
        folder_id = Globals.report_folder_id
        drive = build('drive', 'v3', credentials=self.get_creds(SCOPES_DRIVE))
        gs = gspread.authorize(self.get_creds(SCOPES_SHEETS))
        sheet_id = None
        if os.path.exists(self.report_path + 'logs\\_gdrive_log.txt'):
            with open(self.report_path + 'logs\\_gdrive_log.txt') as file:
                sheet_id = file.readline()
        else:
            sheet_id = gs.copy(template_id, title=self.name, copy_permissions=True).id

            file_metadata = {
                'name': self.name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': template_id
            }
            file = drive.files().get(fileId=sheet_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))
            # Move the file to the new folder
            file = drive.files().update(fileId=sheet_id,
                                        addParents=folder_id,
                                        removeParents=previous_parents,
                                        fields='id, parents').execute()

            with open(self.report_path + 'logs\\_gdrive_log.txt', mode='a+', encoding='utf8') as file:
                file.write(sheet_id)

        '''titles_list = []
        for spreadsheet in gs.openall(self.name):
            titles_list.append([spreadsheet.title, spreadsheet.id, spreadsheet.updated])
        
               
        for sheet in titles_list:
            if self.name in sheet:
                # DELETE SHEETS IF EXIST
                gs.del_spreadsheet(sheet[1])
        if titles_list.__len__() > 1:
            for sheet in titles_list:
                if self.name in sheet:
                    # DELETE SHEETS IF EXIST
                    gs.del_spreadsheet(sheet[1])
            gs = gspread.authorize(self.get_creds(self, SCOPES_SHEETS))
            # gs.create(title=self.file_name, folder_id=folder.get('id'))
            sheet_id = gs.copy(template_id, title=self.name, copy_permissions=True).id
        elif titles_list.__len__() == 1:
            sheet_id = gs.open_by_key(titles_list[1])'''

        # for title in titles_list:
        #    if self.name in title:
        # DELETE SHEETS IF EXIST
        # gs.del_spreadsheet(me[1])

        '''file_metadata = {
            'name': self.name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': template_id
        }'''
        # folder = drive.files().create(body=file_metadata, fields='id').execute()

        # CREATE FROM TEMPLATE
        sheet = gs.open_by_key(sheet_id)

        # source.duplicate_sheet(source.id, new_sheet_name=self.folder_name)
        # titles_list = []
        # for spreadsheet in gs.openall():
        #    titles_list.append(spreadsheet.title)
        worksheet = None
        sheet_range = ''
        if self.report_type == 'dash':
            worksheet = sheet.get_worksheet(1)
            sheet_range = 'DASHBOARD!A4:Z1000'
        if self.report_type == 'axe_c_summary':
            worksheet = sheet.get_worksheet(2)
            sheet_range = 'AXE!A10:Z1000'
        if self.report_type == 'lighthouse':
            worksheet = sheet.get_worksheet(3)
            sheet_range = 'LIGHTHOUSE!A10:Z1000'
        if self.report_type == 'pdf_internal':
            worksheet = sheet.get_worksheet(4)
            sheet_range = worksheet.title
        if self.report_type == 'pdf_external':
            worksheet = sheet.get_worksheet(5)
            sheet_range = worksheet.title
        '''if self.report_type == 'axe_c':
            worksheet = sheet.get_worksheet(6)
            sheet_range = worksheet.title'''
        # sheet.del_worksheet(wsheet)
        # wsheet.de.update_title('NNNNNN')

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
            clear = sheets.spreadsheets().values().clear(
                spreadsheetId=sheet.id, range=sheet_range, body={}).execute()

            result = sheets.spreadsheets().values().update(
                spreadsheetId=sheet.id, range=sheet_range,
                valueInputOption=value_input_option, body=body).execute()

            # Read CSV file contents

            '''
            gc = gspread.authorize(credentials=self.get_creds(SCOPES_SHEETS))
            content = open(filepath, 'r').read()

            gs.import_csv(sheet.get_worksheet(8), content)
            '''
            print('{0} cells updated.'.format(result.get('updatedCells')))
            try:
                filepath = self.report_path + 'AXE\\Chrome\\AXEChrome_REPORT.csv'
                self.paste_csv(filepath, sheet, 'AXE DATA (CHROME)!A1')
            except Exception as e:
                print(e.__str__())
            try:
                filepath = self.report_path + 'AXE\\Firefox\\AXEFirefox_REPORT.csv'
                self.paste_csv(filepath, sheet, 'AXE DATA (FIREFOX)!A1')
            except Exception as e:
                print(e.__str__())
            try:
                filepath = self.report_path + 'LIGHTHOUSE\\LIGHTHOUSE_REPORT.csv'
                self.paste_csv(filepath, sheet, 'LIGHTHOUSE DATA!A1')
            except Exception as e:
                print(e.__str__())
            try:
                filepath = self.report_path + 'PDF\\internal_pdf_a.csv'
                self.paste_csv(filepath, sheet, 'PDF INTERNAL DATA!A1')
            except Exception as e:
                print(e.__str__())
            try:
                filepath = self.report_path + 'PDF\\external_pdf_a.csv'
                self.paste_csv(filepath, sheet, 'PDF EXTERNAL DATA!A1')
            except Exception as e:
                print(e.__str__())

        # spreadsheets = build('sheets', 'v4', credentials=self.get_creds(self, SCOPES_SHEETS))

    def paste_csv(self, csvfile, sheet, cell):
        import gspread as gs

        '''
        csvFile - path to csv file to upload
        sheet - a gspread.Spreadsheet object
        cell - string giving starting cell, optionally including sheet/tab name
          ex: 'A1', 'MySheet!C3', etc.
        '''
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
        json = Globals.base_folder + 'credentials.json'
        # path = SCOPE.__str__().split('/')[SCOPE.__str__().split('/').__len__() - 1][:-2] + '.pickle'
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
    '''results = drive.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])'''
    # CREATE FOLDER
    drive = build('drive', 'v3', credentials=self.get_creds(SCOPES_DRIVE))
    file_metadata = {
        'name': self.folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.files().create(body=file_metadata, fields='id').execute()
    # print('Folder ID: %s' % folder.get('id'))

    # CREATE SPREADSHEET
    '''body = {
        'name': self.folder_name,
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }

    body["parents"] = [
        {
            'kind': 'drive#fileLink',
            'id': folder.get('id')
        }
    ]
    req = drive.files().create(body=body)
    spreadsheet = req.execute()

    # Get id of fresh sheet
    spread_id = spreadsheet["id"]'''

    file_metadata = {
        'name': self.folder_name,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [folder.get('id')]
    }

    '''spreadsheet = {
        'properties': {
            'title': self.file_name,
            'parents': [folder.get('id')]
        }
    }

    body = []
    body["parents"] = [
        {
            'title': self.file_name,
            'kind': 'drive#fileLink',
            'id': folder.get('id')
        }
    ]
    spreadsheet = spreadsheets.spreadsheets().create(body=body,
                                                     fields='spreadsheetId'
                                                     ).execute()
    print('Spreadsheet ID: {0}'.format(spreadsheet.get('spreadsheetId')))'''
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
