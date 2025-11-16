"""
Tool for managing user preferences.
"""
from .preferences import (
    load_preferences,
    save_preferences,
    get_default_preferences,
    get_user_email,
    set_user_email,
    PREFERENCES_FILE,
)
from google.adk.tools import FunctionTool


def set_user_preference(key: str, value: str) -> str:
    """
    Sets a user preference and saves it to the preferences file.
    
    Args:
        key: The preference key to set (e.g., 'user_email', 'email_signature')
        value: The value to set
        
    Returns:
        A status message indicating success or failure.
    """
    try:
        prefs = load_preferences()
        
        # Handle nested keys like "work_hours.start"
        if "." in key:
            keys = key.split(".")
            current = prefs
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        else:
            prefs[key] = value
        
        if save_preferences(prefs):
            # Return a confirmation including the file path so you know where it was written
            return f"✓ Preference '{key}' has been set to '{value}'. (saved to: {PREFERENCES_FILE})"
        else:
            return f"✗ Error saving preference '{key}'."
    except Exception as e:
        return f"✗ Error setting preference: {e}"


def get_user_preference(key: str) -> str:
    """
    Gets a user preference value.
    
    Args:
        key: The preference key to retrieve
        
    Returns:
        The preference value or an error message.
    """
    try:
        prefs = load_preferences()
        
        # Handle nested keys
        if "." in key:
            keys = key.split(".")
            current = prefs
            for k in keys:
                current = current.get(k, {})
            return str(current)
        else:
            value = prefs.get(key, "Not set")
            return str(value)
    except Exception as e:
        return f"Error retrieving preference: {e}"


def list_preferences() -> str:
    """
    Lists all user preferences in a readable format.
    
    Returns:
        A formatted string of all preferences.
    """
    try:
        prefs = load_preferences()
        result = "=== Your Preferences ===\n"
        
        def format_dict(d, indent=0):
            lines = []
            for key, value in d.items():
                prefix = "  " * indent
                if isinstance(value, dict):
                    lines.append(f"{prefix}{key}:")
                    lines.extend(format_dict(value, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: {value}")
            return lines
        
        result += "\n".join(format_dict(prefs))
        return result
    except Exception as e:
        return f"Error listing preferences: {e}"


def reset_preferences() -> str:
    """
    Resets all preferences to defaults.
    
    Returns:
        A status message.
    """
    try:
        default_prefs = get_default_preferences()
        if save_preferences(default_prefs):
            return "✓ Preferences have been reset to defaults."
        else:
            return "✗ Error resetting preferences."
    except Exception as e:
        return f"Error resetting preferences: {e}"


# Create FunctionTools
set_preference_tool = FunctionTool(set_user_preference)
set_preference_tool.name = "set_preference"
set_preference_tool.description = (
    "Sets a user preference and saves it. "
    "Examples: set_preference('user_email', 'your@email.com'), "
    "set_preference('email_signature', 'Best regards'). "
    "Use this to configure your preferences permanently."
)

get_preference_tool = FunctionTool(get_user_preference)
get_preference_tool.name = "get_preference"
get_preference_tool.description = (
    "Retrieves a user preference value. "
    "Examples: get_preference('user_email'), get_preference('work_hours.start')"
)

list_preferences_tool = FunctionTool(list_preferences)
list_preferences_tool.name = "list_preferences"
list_preferences_tool.description = "Lists all currently saved user preferences."

reset_preferences_tool = FunctionTool(reset_preferences)
reset_preferences_tool.name = "reset_preferences"
reset_preferences_tool.description = "Resets all preferences to default values."
