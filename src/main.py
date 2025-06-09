import sys
import webbrowser
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from env import Settings

settings = Settings()

class FileToGoogleConverter:
    def __init__(self):
        self.service_account_file = settings.google_service_account_file
        self.docs_folder_id = settings.google_docs_folder_id
        self.sheets_folder_id = settings.google_sheets_folder_id
        self.slides_folder_id = settings.google_slides_folder_id
        
        self.scopes = ['https://www.googleapis.com/auth/drive']
        self.credentials = Credentials.from_service_account_file(
            self.service_account_file, scopes=self.scopes
        )
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
    
    def get_file_config(self, file_path):
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.docx':
            return {
                'mime_type': 'application/vnd.google-apps.document',
                'source_mime': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'folder_id': self.docs_folder_id,
                'url_base': 'https://docs.google.com/document/d/'
            }
        elif file_ext in ['.xlsx', '.xls']:
            return {
                'mime_type': 'application/vnd.google-apps.spreadsheet',
                'source_mime': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if file_ext == '.xlsx' else 'application/vnd.ms-excel',
                'folder_id': self.sheets_folder_id,
                'url_base': 'https://docs.google.com/spreadsheets/d/'
            }
        elif file_ext in ['.pptx', '.ppt']:
            return {
                'mime_type': 'application/vnd.google-apps.presentation',
                'source_mime': 'application/vnd.openxmlformats-officedocument.presentationml.presentation' if file_ext == '.pptx' else 'application/vnd.ms-powerpoint',
                'folder_id': self.slides_folder_id,
                'url_base': 'https://docs.google.com/presentation/d/'
            }
        else:
            return None
    
    def upload_and_convert(self, file_path):
        config = self.get_file_config(file_path)
        if not config:
            return None
            
        file_name = Path(file_path).stem
        
        file_metadata = {
            'name': file_name,
            'parents': [config['folder_id']] if config['folder_id'] else [],
            'mimeType': config['mime_type']
        }
        
        media = MediaFileUpload(
            file_path,
            mimetype=config['source_mime'],
            resumable=True
        )
        
        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id'), config['url_base']
    
    def open_document(self, file_id, url_base):
        url = f"{url_base}{file_id}/edit"
        webbrowser.open(url)
    
    def process_file(self, file_path):
        if not Path(file_path).exists():
            return
        
        result = self.upload_and_convert(file_path)
        if not result:
            return
            
        file_id, url_base = result
        self.open_document(file_id, url_base)

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    file_path = sys.argv[1]
    converter = FileToGoogleConverter()
    converter.process_file(file_path)

if __name__ == "__main__":
    main()