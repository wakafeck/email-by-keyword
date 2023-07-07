import os
import base64
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Set up the Gmail API client
creds = Credentials.from_authorized_user_file('credentials.json')
service = build('gmail', 'v1', credentials=creds)

# Define the keyword to search for
keyword = 'important'  # Replace with your desired keyword

# Function to decode the message body from base64
def decode_message_body(message):
    data = message['payload']['body']['data']
    if 'attachmentId' in message['payload']['body']:
        attachment = service.users().messages().attachments().get(
            userId='me',
            messageId=message['id'],
            id=message['payload']['body']['attachmentId']
        ).execute()
        data = attachment['data']
    return base64.urlsafe_b64decode(data).decode()

# Function to save the matching messages
def save_matching_messages(messages):
    for message in messages:
        msg_id = message['id']
        msg = service.users().messages().get(userId='me', id=msg_id).execute()
        subject = [header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'][0]
        body = decode_message_body(msg)
        
        # Save the matching messages
        if re.search(keyword, subject, re.IGNORECASE) or re.search(keyword, body, re.IGNORECASE):
            with open(f"matching_email_{msg_id}.txt", 'w') as file:
                file.write(f"Subject: {subject}\n\n{body}")
            print(f"Matching email saved: {msg_id}")

# Fetch all inbox messages
response = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
messages = response.get('messages', [])

# Process and save the matching messages
if messages:
    save_matching_messages(messages)
else:
    print("No inbox messages found.")
