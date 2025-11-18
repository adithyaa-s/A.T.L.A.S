import base64
import email
from .email_utils import get_gmail_service
from google.adk.tools import FunctionTool


def get_full_email(message_id: str) -> str:
    """
    Retrieves the full content of an email by its message ID.
    
    Args:
        message_id: The ID of the email message (found using read_meeting_emails).
        
    Returns:
        The full email content (subject, from, date, and body), or an error message.
    """
    service = get_gmail_service()
    if not service:
        return "ERROR: Could not connect to Gmail service."
    
    try:
        # Get the full message in raw format
        message = service.users().messages().get(userId='me', id=message_id, format='raw').execute()
        
        # Decode the raw message
        msg_str = base64.urlsafe_b64decode(message['raw']).decode('utf-8')
        email_message = email.message_from_string(msg_str)
        
        # Extract headers
        subject = email_message.get('Subject', 'No Subject')
        sender = email_message.get('From', 'Unknown')
        date = email_message.get('Date', 'Unknown')
        
        # Extract body (handle both plain text and HTML)
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                elif part.get_content_type() == 'text/html' and not body:
                    # Fallback to HTML if no plain text
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        # Format the output
        result = f"""
=== Full Email ===
Subject: {subject}
From: {sender}
Date: {date}
Message ID: {message_id}

--- Body ---
{body.strip()}
"""
        return result
        
    except Exception as e:
        return f"An error occurred while retrieving the full email: {e}. Please ensure the message_id is valid."


# Create the FunctionTool
get_full_email_tool = FunctionTool(get_full_email)
get_full_email_tool.name = "get_full_email"
get_full_email_tool.description = (
    "Retrieves the full content (including complete body) of an email by its message ID. "
    "Use this to read the complete email content, not just the snippet."
)
