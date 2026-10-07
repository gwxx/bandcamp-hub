import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from app.config import CREDENTIALS_PATH, TOKEN_PATH, logger

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_oauth_flow(redirect_uri: str) -> Flow:
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError("尚未上傳 credentials.json 憑證檔案。")
    
    with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        client_config = json.load(f)
    
    return Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

def get_credentials() -> Credentials | None:
    if not TOKEN_PATH.exists():
        return None
    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        return creds if creds.valid else None
    except RefreshError as e:
        logger.error(f"Google Token 已失效或遭撤銷，自動清理: {e}")
        disconnect_account()
        return None
    except Exception as e:
        logger.error(f"Google 憑證處理異常: {e}")
        return None

def build_gmail_service():
    creds = get_credentials()
    if not creds:
        return None
    return build("gmail", "v1", credentials=creds)

def disconnect_account():
    if TOKEN_PATH.exists():
        TOKEN_PATH.unlink()
    logger.info("已清除本地 Token 授權檔。")
