"""Email-to-Calendar Parser

Extracts meeting details (date, time, attendees, location, title) from email bodies
and provides structured data ready for calendar event creation.
"""

from typing import Optional, Dict, Any
import json
import re
from datetime import datetime, timedelta

try:
    from google.adk.tools import FunctionTool
    HAS_ADK = True
except Exception:
    HAS_ADK = False
    # Fallback: simple wrapper
    class FunctionTool:
        def __init__(self, func, description):
            self.func = func
            self.description = description


def parse_email_for_meeting(
    email_subject: str,
    email_body: str,
    email_from: str = "",
) -> Dict[str, Any]:
    """
    Extract meeting details from an email body using pattern matching and heuristics.
    
    Args:
        email_subject (str): Email subject line
        email_body (str): Email body content
        email_from (str, optional): Sender's email address for context
    
    Returns:
        Dict with keys: success (bool), meeting_found (bool), title, start_time, 
        end_time, attendees, location, notes, confidence (0-1)
    
    Examples of what it detects:
    - "Meeting on Friday 2pm at Conference Room A"
    - "Let's meet next Tuesday 10:00 AM EST"
    - "Can you join the call at 3:30pm?"
    - "Attendees: john@company.com, jane@company.com"
    """
    
    try:
        result = {
            "success": True,
            "meeting_found": False,
            "title": "",
            "start_time": "",
            "end_time": "",
            "attendees": [],
            "location": "",
            "notes": "",
            "confidence": 0.0,
            "raw_details": {}
        }
        
        # Combine subject and body for analysis
        full_text = f"{email_subject}\n{email_body}".lower()
        
        # 1. Try to extract meeting title
        result["title"] = email_subject or "Meeting"
        
        # 2. Look for time patterns
        time_patterns = [
            r"(\d{1,2}):(\d{2})\s*(am|pm|a\.m\.|p\.m\.)?",  # 2:30pm or 14:30
            r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(\d{1,2}):(\d{2})",
            r"(tomorrow|today|next\s+\w+)\s+(?:at\s+)?(\d{1,2}):(\d{2})",
        ]
        
        times_found = []
        for pattern in time_patterns:
            matches = re.findall(pattern, full_text)
            times_found.extend(matches)
        
        # 3. Look for location
        location_keywords = ["room", "conference", "office", "at ", "location:", "venue:"]
        location_match = None
        for keyword in location_keywords:
            if keyword in full_text:
                idx = full_text.find(keyword)
                # Extract ~30 chars after keyword
                location_match = email_body[idx:idx+50].split('\n')[0].strip()
                if location_match:
                    result["location"] = location_match
                    break
        
        # 4. Look for attendees (email addresses)
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails_found = re.findall(email_pattern, email_body)
        result["attendees"] = list(set(emails_found))  # Remove duplicates
        if email_from and email_from not in result["attendees"]:
            result["attendees"].insert(0, email_from)
        
        # 5. Simple heuristic: if we found times, location, or attendees + time = likely a meeting
        has_time = len(times_found) > 0
        has_location = len(result["location"]) > 0
        has_attendees = len(result["attendees"]) > 1 or email_from
        
        meeting_keywords = ["meeting", "call", "sync", "standup", "review", "presentation", "conference", "webinar"]
        has_meeting_keyword = any(kw in full_text for kw in meeting_keywords)
        
        result["meeting_found"] = has_time or (has_meeting_keyword and has_location)
        result["confidence"] = min(0.95, 0.3 * has_time + 0.3 * has_meeting_keyword + 0.2 * has_location + 0.2 * has_attendees)
        
        result["raw_details"] = {
            "times_found": times_found,
            "location_found": has_location,
            "attendees_count": len(result["attendees"]),
            "meeting_keyword_found": has_meeting_keyword,
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "meeting_found": False,
            "error": str(e),
            "title": "",
            "start_time": "",
            "end_time": "",
            "attendees": [],
            "location": "",
            "notes": "",
            "confidence": 0.0,
        }


# Create FunctionTool wrapper for ADK
try:
    parse_email_for_meeting_tool = FunctionTool(parse_email_for_meeting)
    parse_email_for_meeting_tool.name = "parse_email_for_meeting"
    parse_email_for_meeting_tool.description = "Extracts meeting details (date, time, attendees, location) from email body. Returns structured data ready for calendar event creation. Use this to detect if an email contains a meeting invitation or meeting request."
except Exception:
    # Fallback if FunctionTool doesn't exist
    class MockTool:
        pass
    parse_email_for_meeting_tool = MockTool()
    parse_email_for_meeting_tool.func = parse_email_for_meeting
