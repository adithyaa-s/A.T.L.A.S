import os
import pickle
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these scopes, delete the file gmail_token.json.
# Use a unified scope set used across quickstart and utilities. Include read, send and modify.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
]

# Get the absolute path to the project root (two levels up from this file)
# This file is at JARVIS/tools/email/email_utils.py
# So we go up to get to JARVIS directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Path for Gmail token storage (absolute path)
TOKEN_PATH = PROJECT_ROOT / "credentials" / "gmail_token.json"
CREDENTIALS_PATH = PROJECT_ROOT / "credentials.json"

def get_gmail_service():
    """Shows how to authenticate and return a Google API service."""
    creds = None
    # The file gmail_token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_info(
            json.loads(TOKEN_PATH.read_text()), SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Assumes credentials.json is in the current directory
            # Use the configured CREDENTIALS_PATH (absolute) instead of a literal path
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"An error occurred while building the Gmail service: {e}")
        return None