from __future__ import print_function

import os

from dotenv import load_dotenv
from googleapiclient.discovery import build

from google.oauth2 import service_account

import functions

load_dotenv()
sheet_id = os.environ.get("SHEET_ID")


def main():
    SERVICE_ACCOUNT_FILE = 'keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # The ID spreadsheet.
    SAMPLE_SPREADSHEET_ID = sheet_id

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    users = []
    for p in functions.sortedPeer:
        users.append([p.name, p.transfer, p.active])

    body = {
        'values': users
    }

    sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=functions.conf_name + "!A2", body=body,
                          valueInputOption="USER_ENTERED").execute()
