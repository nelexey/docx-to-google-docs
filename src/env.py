from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    google_service_account_file: str
    google_docs_folder_id: Optional[str] = None
    google_sheets_folder_id: Optional[str] = None
    google_slides_folder_id: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False