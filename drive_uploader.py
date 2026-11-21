import os
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = os.getenv("FOLDER_ID")

# Dosya yolu hatası olmaması için klasör yolunu otomatik bulur
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')

def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def upload_docx_to_drive(file_path: str, drive_file_name: str) -> str:
    service = get_drive_service()

    file_metadata = {
        'name': drive_file_name,
        'parents': [FOLDER_ID]
    }
    media = MediaFileUpload(
        file_path,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        resumable=True
    )

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    return uploaded_file.get('webViewLink')