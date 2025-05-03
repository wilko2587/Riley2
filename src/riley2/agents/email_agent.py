import logging
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path
from riley2.core.llm_backend import summarize_text
from riley2.core.logger_utils import logger

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    logger.debug("Authenticating Gmail API...")
    base_path = Path(__file__).resolve().parent.parent / "secrets"
    creds = None
    token_path = base_path / "token_gmail.json"
    creds_path = base_path / "credentials.json"
    if token_path.exists():
        logger.debug("Loading credentials from token file.")
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.debug("Refreshing expired credentials.")
            creds.refresh(Request())
        else:
            logger.debug("Initiating new OAuth flow.")
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            logger.debug("Saving new credentials to token file.")
            token.write(creds.to_json())
    logger.info("Gmail API authenticated successfully.")
    return build('gmail', 'v1', credentials=creds)

def email_download_chunk(start_date: str, end_date: str):
    logger.debug(f"Downloading emails from {start_date} to {end_date}.")
    service = authenticate_gmail()
    query = f"after:{start_date} before:{end_date}"
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=20).execute()
        messages = results.get('messages', [])
        logger.info(f"Retrieved {len(messages)} emails.")
    except Exception as e:
        logger.error(f"Error retrieving emails: {e}")
        return "Error retrieving emails."

    output = []
    for msg in messages:
        try:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')
            snippet = msg_data.get('snippet', "")
            output.append(f"From: {sender}\nSubject: {subject}\n{snippet}\n")
        except Exception as e:
            logger.error(f"Error processing email ID {msg['id']}: {e}")
    logger.debug(f"Processed {len(output)} emails.")
    return "\n---\n".join(output) or "No emails found."

def email_filter_by_sender(raw_emails: str, sender_email: str):
    logger.debug(f"Filtering emails by sender: {sender_email}")
    chunks = raw_emails.split('---')
    filtered = [chunk for chunk in chunks if sender_email.lower() in chunk.lower()]
    logger.info(f"Found {len(filtered)} emails from {sender_email}.")
    return "\n---\n".join(filtered) or f"No emails found from {sender_email}."

def email_summarize_batch(raw_emails: str):
    logger.debug(f"Summarizing email batch of size: {len(raw_emails)} characters.")
    summary = summarize_text(raw_emails)
    logger.debug(f"Email summary: {summary}")
    return summary