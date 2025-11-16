# calendar_tools.py
from google.adk.tools import FunctionTool

# --- Import all calendar functions from their respective files ---
# IMPORTANT: Adjust the import paths below if your file names are different!
from .create_event import create_event
from .delete_event import delete_event
from .edit_event import edit_event
from .list_events import list_events
from .calendar_utils import get_current_time # get_current_time is usually imported and used by the agent itself


# ----------------------------------------------------
# 1. DEFINE FunctionTool OBJECTS
# ----------------------------------------------------

# --- create_event Tool ---
create_event_tool = FunctionTool(create_event) 
create_event_tool.name = "create_event"
create_event_tool.description = "Add a new event to your calendar. Requires summary, start_time, and end_time (YYYY-MM-DD HH:MM format)."

# --- delete_event Tool ---
delete_event_tool = FunctionTool(delete_event) 
delete_event_tool.name = "delete_event"
delete_event_tool.description = "Remove an event from your calendar. Requires the event_id and explicit confirmation (confirm=True)."

# --- edit_event Tool ---
edit_event_tool = FunctionTool(edit_event) 
edit_event_tool.name = "edit_event"
edit_event_tool.description = "Edit an existing event (change title, start_time, or end_time). Requires event_id. Pass empty strings for fields you don't want to change."

# --- list_events Tool ---
list_events_tool = FunctionTool(list_events) 
list_events_tool.name = "list_events"
list_events_tool.description = "Show events from your calendar for a specific period. Requires start_date (YYYY-MM-DD, or empty string for today) and days (int: 1 for today, 7 for a week, etc.)."

# --- find_free_time (Placeholder - You need to write this function) ---
def find_free_time(start_date: str, end_date: str) -> dict:
    """Placeholder function for finding free time."""
    return {"status": "error", "message": "find_free_time tool is not yet implemented."}

find_free_time_tool = FunctionTool(find_free_time)
find_free_time_tool.name = "find_free_time"
find_free_time_tool.description = "Find available free time slots in your calendar between two dates. Requires start_date and end_date in YYYY-MM-DD format."


# ----------------------------------------------------
# 2. LIST OF TOOLS FOR EASY IMPORT INTO agent.py
# ----------------------------------------------------

CALENDAR_TOOLS = [
    create_event_tool,
    delete_event_tool,
    edit_event_tool,
    list_events_tool,
    find_free_time_tool,
]