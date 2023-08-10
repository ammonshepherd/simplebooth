from __future__ import print_function

import os.path

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def upload_to_folder(cred_file, folder_id, file_name, mime_type):
    creds = service_account.Credentials.from_service_account_file(cred_file)
    scoped = creds.with_scopes(SCOPES)
    try:
        service = build("drive", "v3", credentials=scoped)

        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaFileUpload(file_name, mimetype=mime_type, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='webViewLink').execute()
        print(file.get('webViewLink'))
        return file.get('webViewLink')

    except HttpError as error:
        print(f'Thus an error: {error}')
        return None



if __name__ == '__main__':
    upload_to_folder(cred_file='service_account.json',
                     folder_id='1FEH74jojf7WPOYk0ILqexKMs-ezGwGnE',
                     file_name='simplebooth-icon.png', mime_type='image/png')
