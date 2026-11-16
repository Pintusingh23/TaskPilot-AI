
import os
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Gmail permissions
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly"
]


# --------------------------------
# 1. GMAIL AUTHENTICATION
# --------------------------------

def authenticate_gmail():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )

        creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
        token.write(creds.to_json())

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    print("Gmail authentication successful!")

    return service


# --------------------------------
# 2. SEND EMAIL
# --------------------------------

def send_email(service, recipient, subject, body):

    message = MIMEText(body)

    message["to"] = recipient
    message["subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    result = service.users().messages().send(
        userId="me",
        body={"raw": encoded_message}
    ).execute()

    return result


# --------------------------------
# 3. READ RECENT INBOX EMAILS
# --------------------------------

def read_recent_emails(service, max_results=5):

    results = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        q="in:inbox"
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        return []

    email_list = []

    for message in messages:

        email = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="metadata",
            metadataHeaders=[
                "From",
                "Subject",
                "Date"
            ]
        ).execute()

        headers = email.get(
            "payload", {}
        ).get("headers", [])

        email_data = {}

        for header in headers:
            email_data[header["name"]] = header["value"]

        email_list.append({
            "from": email_data.get("From", "Unknown"),
            "subject": email_data.get("Subject", "No Subject"),
            "date": email_data.get("Date", "Unknown")
        })

    return email_list


# --------------------------------
# 4. TEST GMAIL TOOL
# --------------------------------

if __name__ == "__main__":

    try:

        service = authenticate_gmail()

        emails = read_recent_emails(service, 5)

        print("\n===== YOUR RECENT EMAILS =====")

        if not emails:
            print("Your inbox is empty.")

        else:

            for email in emails:

                print("\nFrom:", email["from"])
                print("Subject:", email["subject"])
                print("Date:", email["date"])

        print("\nGmail inbox reading completed!")

    except Exception as error:

        print("\nSomething went wrong!")
        print("Error:", error)
