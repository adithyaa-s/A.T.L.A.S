import base64
from email.mime.text import MIMEText
from .email_utils import get_gmail_service
from google.adk.tools import FunctionTool
from ..preferences import get_user_email, get_email_signature


def send_email(to: str, subject: str, message_body: str) -> str:
    """
    Sends a new email to one or more recipients.
    
    Args:
        to: The recipient email address (or comma-separated list of addresses).
             Can also be "myself" to send to the user's email from preferences.
        subject: The subject line of the email.
        message_body: The body content of the email.
        
    Returns:
        A status message indicating success or failure.
    """
    service = get_gmail_service()
    if not service:
        return "ERROR: Could not connect to Gmail service."
    
    try:
        # Handle "myself" keyword
        if to.lower() == "myself":
            to = get_user_email()
            if not to:
                return "ERROR: No email address set in preferences. Use set_preference('user_email', 'your@email.com') first."
        
        # Get user's signature if not already in message body
        signature = get_email_signature()
        if signature and signature not in message_body:
            message_body = f"{message_body}\n\n{signature}"
        
        # Create the email message
        message = MIMEText(message_body)
        message['to'] = to
        message['subject'] = subject
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send the message
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        
        return f"✓ Successfully sent email to {to} with subject '{subject}'."
        
    except Exception as e:
        return f"✗ Error sending email: {e}. Please check the recipient address and try again."


# Create the FunctionTool
send_email_tool = FunctionTool(send_email)
send_email_tool.name = "send_email"
send_email_tool.description = (
    "Sends a new email to one or more recipients. "
    "Use 'myself' to send to your email from preferences. "
    "Requires 'to' (recipient email or 'myself'), 'subject', and 'message_body'. "
    "Automatically adds your signature."
)
