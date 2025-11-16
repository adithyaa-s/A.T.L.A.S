import base64
from email.mime.text import MIMEText
from .email_utils import get_gmail_service
from google.adk.tools import FunctionTool

def read_meeting_emails(max_results: int = 5) -> str:
    """
    Reads the 'max_results' most recent emails from the user's inbox 
    that have the keyword 'meeting' in the subject line.
    
    Args:
        max_results: The maximum number of emails to retrieve. Defaults to 5.
        
    Returns:
        A summarized string containing the sender, subject, and snippet of 
        each matching email, or an error message.
    """
    service = get_gmail_service()
    if not service:
        return "ERROR: Could not connect to Gmail service."

    try:
        # Construct the query to find emails with 'meeting' in the subject line
        query = 'subject:meeting'
        
        # Get the list of messages matching the query
        response = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = response.get('messages', [])
        
        if not messages:
            return "No emails found with 'meeting' in the subject line."
            
        summary = "Found the following meeting-related emails:\n"
        
        # Retrieve details for each message
        for message in messages:
            # Use format='metadata' to get the subject/sender/date quickly
            msg = service.users().messages().get(userId='me', id=message['id'], format='metadata', metadataHeaders=['From', 'Subject', 'Date']).execute()
            
            headers = {header['name']: header['value'] for header in msg['payload']['headers']}
            
            summary += (
                f"  - ID: {msg['id']}\n"
                f"    From: {headers.get('From', 'N/A')}\n"
                f"    Subject: {headers.get('Subject', 'N/A')}\n"
                f"    Date: {headers.get('Date', 'N/A')}\n"
                f"    Snippet: {msg.get('snippet', 'No snippet available.')}\n"
                f"    --------------------\n"
            )
            
        return summary
        
    except Exception as e:
        return f"An error occurred while reading emails: {e}"


# ----------------------------------------------------
# ADK Tool Definitions for Agent Orchestration
# ----------------------------------------------------

# read_meeting_emails_tool = FunctionTool(
#     callable=read_meeting_emails,
#     name="read_meeting_emails",
#     description="Reads the most recent emails that have 'meeting' in the subject line to provide a quick summary. Useful for checking upcoming events.",
# )

read_meeting_emails_tool = FunctionTool(read_meeting_emails)

read_meeting_emails_tool.name = "read_meeting_emails"
read_meeting_emails_tool.description = (
    "Reads the most recent emails that have 'meeting' in the subject line to provide a quick summary. "
    "Useful for checking upcoming events."
)

# You would import these tool objects into your CommunicationAgent
# Example: communication_agent = LlmAgent(..., tools=[read_meeting_emails_tool, send_email_reply_tool])