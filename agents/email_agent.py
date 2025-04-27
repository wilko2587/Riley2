from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path
from core.llm_backend import summarize_text

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    base_path = Path(__file__).resolve().parent.parent / "secrets"
    creds = None
    token_path = base_path / "token_gmail.json"
    creds_path = base_path / "credentials.json"
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def email_download_chunk(start_date: str, end_date: str):
    # Download emails between start_date and end_date (format: YYYY/MM/DD)
    service = authenticate_gmail()
    query = f"after:{start_date} before:{end_date}"
    results = service.users().messages().list(userId='me', q=query, maxResults=20).execute()
    messages = results.get('messages', [])

    output = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data.get("payload", {}).get("headers", [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')
        snippet = msg_data.get('snippet', "")
        output.append(f"From: {sender}\nSubject: {subject}\n{snippet}\n")
    return "\n---\n".join(output) or "No emails found."

def email_filter_by_sender(raw_emails: str, sender_email: str):
    # Return only messages from a particular sender in a blob of raw emails
    chunks = raw_emails.split('---')
    filtered = [chunk for chunk in chunks if sender_email.lower() in chunk.lower()]
    return "\n---\n".join(filtered) or f"No emails found from {sender_email}."

def email_summarize_batch(raw_emails: str):
    # Summarize a batch of emails
    return summarize_text(raw_emails)