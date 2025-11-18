import base64
import email
from email.mime.text import MIMEText
from email.utils import parseaddr
from .email_utils import get_gmail_service
from google.adk.tools import FunctionTool


def send_email_reply(thread_or_message_id: str, message_body: str) -> str:
    """
    Sends a reply to an existing email thread or message.

    This function is robust: it accepts either a message ID or a thread ID.
    If the provided id is invalid/unavailable it will try to fall back to
    sending a new message to the original sender.

    Args:
        thread_or_message_id: The thread ID or message ID to reply to.
        message_body: The content of the reply message.

    Returns:
        A status message indicating success or failure.
    """
    service = get_gmail_service()
    if not service:
        return "ERROR: Could not connect to Gmail service."

    original_sender = None
    reply_subject = None
    thread_id = None

    try:
        # First, try to treat the ID as a message ID
        try:
            original_msg = service.users().messages().get(userId='me', id=thread_or_message_id, format='raw').execute()
            thread_id = original_msg.get('threadId')
        except Exception:
            original_msg = None

        # If not found as a message, try as a thread ID and pick the first message
        if not original_msg:
            try:
                thread = service.users().threads().get(userId='me', id=thread_or_message_id, format='full').execute()
                thread_id = thread.get('id')
                messages = thread.get('messages', [])
                if messages:
                    # Use the first message in the thread for headers
                    msg_id = messages[0].get('id')
                    original_msg = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
            except Exception:
                original_msg = None

        # If we have the original message, decode and parse headers
        if original_msg and 'raw' in original_msg:
            msg_str = base64.urlsafe_b64decode(original_msg['raw']).decode('utf-8', errors='ignore')
            original_email = email.message_from_string(msg_str)

            original_sender = original_email.get('From')
            original_subject = original_email.get('Subject', '')
            # Normalize subject
            if original_subject and not original_subject.lower().startswith('re:'):
                reply_subject = f"Re: {original_subject}"
            else:
                reply_subject = original_subject or 'Re:'

            # Prefer the thread id we extracted earlier
            if not thread_id:
                thread_id = original_msg.get('threadId')

        # If we couldn't locate the original message/thread, return informative error
        if not original_sender:
            # Fallback: inform user and attempt nothing further
            return ("ERROR: Original message or thread not found or not accessible. "
                    "I can instead send a new email to the sender if you provide their address.")

        # Extract a clean email address
        recipient = parseaddr(original_sender)[1]

        # Build reply message with proper headers
        reply_message = MIMEText(message_body)
        reply_message['To'] = recipient
        reply_message['Subject'] = reply_subject

        # If original message has a Message-ID header, include In-Reply-To and References
        try:
            msg_str = base64.urlsafe_b64decode(original_msg['raw']).decode('utf-8', errors='ignore')
            parsed = email.message_from_string(msg_str)
            msg_id_hdr = parsed.get('Message-ID')
            if msg_id_hdr:
                reply_message['In-Reply-To'] = msg_id_hdr
                # Set References to the original message-id as a minimal reference
                reply_message['References'] = msg_id_hdr
        except Exception:
            pass

        raw_message = base64.urlsafe_b64encode(reply_message.as_bytes()).decode()

        message_data = {'raw': raw_message}
        if thread_id:
            message_data['threadId'] = thread_id

        # Attempt to send as a reply (with threadId if available)
        service.users().messages().send(userId='me', body=message_data).execute()

        return f"Successfully sent reply to '{recipient}' with subject '{reply_subject}'."

    except Exception as e:
        # If something goes wrong, try fallback: send a new message to the recipient
        try:
            if original_sender:
                recipient = parseaddr(original_sender)[1]
                fallback_msg = MIMEText(message_body)
                fallback_msg['To'] = recipient
                fallback_msg['Subject'] = reply_subject or 'Re: '
                raw_fb = base64.urlsafe_b64encode(fallback_msg.as_bytes()).decode()
                service.users().messages().send(userId='me', body={'raw': raw_fb}).execute()
                return (f"Primary reply failed but a new message was sent to {recipient}. "
                        f"Error: {e}")
        except Exception as e2:
            return f"An error occurred while sending the email reply: {e}. Fallback also failed: {e2}"
        return f"An error occurred while sending the email reply: {e}."


# send_email_reply_tool = FunctionTool(
#     callable=send_email_reply,
#     name="send_email_reply",
#     description="Sends a text reply to a specific email thread. REQUIRES a valid 'thread_id' and the 'message_body'.",
# )
send_email_reply_tool = FunctionTool(send_email_reply)

send_email_reply_tool.name = "send_email_reply"
send_email_reply_tool.description = (
    "Sends a text reply to a specific email thread. REQUIRES a valid 'thread_id' and the 'message_body'."
)