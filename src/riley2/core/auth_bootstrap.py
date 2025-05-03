from riley2.agents.email_agent import authenticate_gmail
from riley2.agents.calendar_agent import authenticate_calendar

def run_auth_bootstrap():
    print("🔐 Checking credentials for Gmail and Calendar...")
    try:
        authenticate_gmail()
        print("✅ Gmail authentication OK")
    except Exception as e:
        print(f"❌ Gmail auth failed: {e}")

    try:
        authenticate_calendar()
        print("✅ Calendar authentication OK")
    except Exception as e:
        print(f"❌ Calendar auth failed: {e}")
