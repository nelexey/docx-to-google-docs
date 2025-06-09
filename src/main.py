import sys
import webbrowser
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from env import Settings

settings = Settings()

class DocxToGoogleDocs:
    def __init__(self):
        self.service_account_file = settings.google_service_account_file
        self.docs_folder_id = settings.google_docs_folder_id
        
        self.scopes = ['https://www.googleapis.com/auth/drive']
        self.credentials = Credentials.from_service_account_file(
            self.service_account_file, scopes=self.scopes
        )
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
    
    def upload_and_convert(self, file_path):
        file_name = Path(file_path).stem
        
        file_metadata = {
            'name': file_name,
            'parents': [self.docs_folder_id] if self.docs_folder_id else [],
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        media = MediaFileUpload(
            file_path,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            resumable=True
        )
        
        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    
    def open_document(self, doc_id):
        url = f"https://docs.google.com/document/d/{doc_id}/edit"
        webbrowser.open(url)
    
    def process_file(self, file_path):
        if not Path(file_path).exists() or not file_path.lower().endswith('.docx'):
            return
        
        doc_id = self.upload_and_convert(file_path)
        self.open_document(doc_id)

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    file_path = sys.argv[1]
    opener = DocxToGoogleDocs()
    opener.process_file(file_path)

if __name__ == "__main__":
    main()