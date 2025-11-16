"""
User preferences system for storing and managing user settings.
"""
import json
from pathlib import Path

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
PREFERENCES_FILE = PROJECT_ROOT / "preferences.json"


def load_preferences() -> dict:
    """Load user preferences from file."""
    if PREFERENCES_FILE.exists():
        try:
            with open(PREFERENCES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading preferences: {e}")
            return get_default_preferences()
    return get_default_preferences()


def save_preferences(prefs: dict) -> bool:
    """Save user preferences to file."""
    try:
        PREFERENCES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump(prefs, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving preferences: {e}")
        return False


def get_default_preferences() -> dict:
    """Return default preferences structure."""
    return {
        "user_email": "adithyaasaravanan.cse2023@citchennai.net",
        "work_hours": {
            "start": "09:00",
            "end": "17:00"
        },
        "availability": {
            "monday": True,
            "tuesday": True,
            "wednesday": True,
            "thursday": True,
            "friday": True,
            "saturday": False,
            "sunday": False
        },
        "preferred_meeting_duration_minutes": 30,
        "busy_keywords": ["busy", "meeting", "unavailable"],
        "auto_reply_preferences": {
            "draft_replies": True,
            "auto_suggest_times": True,
            "include_calendar_check": True
        },
        "email_signature": "Best regards,\nYour Assistant"
    }


def get_user_email() -> str:
    """Get the user's email address from preferences."""
    prefs = load_preferences()
    return prefs.get("user_email", "")


def set_user_email(email: str) -> bool:
    """Set the user's email address in preferences."""
    prefs = load_preferences()
    prefs["user_email"] = email
    return save_preferences(prefs)


def get_work_hours() -> dict:
    """Get user's work hours."""
    prefs = load_preferences()
    return prefs.get("work_hours", {"start": "09:00", "end": "17:00"})


def is_user_available(day_of_week: str) -> bool:
    """Check if user is available on a specific day of the week."""
    prefs = load_preferences()
    availability = prefs.get("availability", {})
    return availability.get(day_of_week.lower(), False)


def should_draft_replies() -> bool:
    """Check if agent should draft replies instead of sending directly."""
    prefs = load_preferences()
    return prefs.get("auto_reply_preferences", {}).get("draft_replies", True)


def should_auto_suggest_times() -> bool:
    """Check if agent should auto-suggest meeting times."""
    prefs = load_preferences()
    return prefs.get("auto_reply_preferences", {}).get("auto_suggest_times", True)


def should_check_calendar() -> bool:
    """Check if agent should check calendar before replying."""
    prefs = load_preferences()
    return prefs.get("auto_reply_preferences", {}).get("include_calendar_check", True)


def get_email_signature() -> str:
    """Get the user's email signature."""
    prefs = load_preferences()
    return prefs.get("email_signature", "")


def update_preference(key: str, value) -> bool:
    """Update a specific preference."""
    prefs = load_preferences()
    prefs[key] = value
    return save_preferences(prefs)
