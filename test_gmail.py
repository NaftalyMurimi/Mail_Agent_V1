from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = 'token.json'

def test_gmail():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    # Get profile info
    profile = service.users().getProfile(userId='me').execute()
    print(f"Connected Gmail: {profile['emailAddress']}")
    print(f"Total messages: {profile['messagesTotal']}")

    # Fetch last 5 emails
    results = service.users().messages().list(
        userId='me',
        maxResults=5,
        q='newer_than:7d'
    ).execute()

    messages = results.get('messages', [])
    print(f"\nEmails from last 7 days found: {len(messages)}")

    for msg in messages[:3]:
        detail = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From']
        ).execute()

        headers = {h['name']: h['value'] for h in detail['payload']['headers']}
        print(f"\n  Subject: {headers.get('Subject', 'No subject')}")
        print(f"  From:    {headers.get('From', 'Unknown')}")

    print("\nGmail connection working ✅")

if __name__ == '__main__':
    test_gmail()