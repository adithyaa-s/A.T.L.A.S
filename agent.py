from google.adk.agents.llm_agent import Agent

from .tools.calender.calender_tools import CALENDAR_TOOLS, get_current_time

from .tools.email.read_email import read_meeting_emails_tool

from .tools.email.send_email import send_email_reply_tool

from .tools.email.compose_email import send_email_tool

from .tools.email.get_full_email import get_full_email_tool

from .tools.email.email_to_calendar import parse_email_for_meeting_tool

# Keep feature removed. Previously imported KEEP_TOOLS from tools.keep.keep_utils

from .tools.manage_preferences import (
    set_preference_tool,
    get_preference_tool,
    list_preferences_tool,
    reset_preferences_tool,
)

from .tools.search import google_search_tool

from .tools.memory import (
    MEMORY_TOOLS,
    store_preference,
    recall_preference,
    search_memory,
    store_user_fact,
    add_important_contact,
    get_important_contacts,
    add_conversation_context,
    recall_conversation_context,
)


from .tools.preferences import (
    should_draft_replies,
    should_auto_suggest_times,
    should_check_calendar,
    get_email_signature,
    get_user_email,
)

MODEL_NAME = 'gemini-2.5-flash-lite-preview-06-17'

email_agent = Agent(
    model=MODEL_NAME,
    name="google_gmail_agent",
    description="Handles Gmail tasks like reading emails, getting full content, sending emails, and parsing meeting invitations",
    instruction=f"""You handle queries related to Gmail. You have access to these tools:
    - `read_emails`: Reads emails matching a specific keyword or query. Returns summaries with snippets.
    - `get_full_email`: Gets the complete content of an email by its message ID. Use this when user needs full details.
    - `parse_email_for_meeting`: Extracts meeting details (date, time, attendees, location) from email body. Use this to detect meeting invitations.
    - `send_email`: Sends a new email to one or more recipients. Use 'myself' to send to your saved email address.
    - `send_email_reply`: Sends a reply to an existing email thread.
    
    ## Smart Email & Meeting Handling
    When user asks to read emails:
    1. First use `read_emails` to find matching emails
    2. Offer to get full content if needed
    3. If email contains meeting details, use `parse_email_for_meeting` to extract: date, time, location, attendees
    4. Offer to create calendar event or draft a reply
    
    When parsing meeting emails:
    - Use `parse_email_for_meeting` to extract structured meeting data
    - If parsing shows high confidence (0.7+), suggest creating a calendar event
    - Show extracted details to user before creating event
    
    If user wants to reply to an email, ALWAYS:
    1. Use `get_full_email` to see the full message and sender details
    2. Check if it contains meeting info using `parse_email_for_meeting`
    3. Check calendar if user asks for meeting (transfer to calendar agent if needed)
    4. Draft a professional reply using the signature: "{get_email_signature()}"
    5. Send the reply using `send_email_reply` with the thread_id
    
    ## Guidelines
    - For reading emails: Ask user what keyword or sender they're looking for if vague. Default to 'meeting' keyword.
    - For meeting detection: Always parse for meeting details when email mentions dates, times, or meeting keywords
    - For replying: ALWAYS get the full email first, then draft and send intelligently.
    - When user says "send to myself", use 'myself' as the 'to' parameter - don't ask for email address.
    - If user's email isn't set and they try to send to 'myself', inform them to set it via preferences first.
    - Be professional and helpful. Always include proper greetings and signatures in replies.
    - If user needs calendar info, coordinate with the calendar agent.
    
    User's current email: {get_user_email() or 'Not set - encourage setting it in preferences'}
    
    Use the available tools to fulfill the user's request. If you encounter an error, provide the exact error message.""",
    tools=[read_meeting_emails_tool, get_full_email_tool, parse_email_for_meeting_tool, send_email_tool, send_email_reply_tool]
)

calendar_agent = Agent(
    model=MODEL_NAME,
    name="google_calender_agent",
    description="Handles Calendar tasks and helps with email scheduling coordination",
    instruction=f"""You handle queries related to Google Calendar and help coordinate meeting scheduling for emails. 
    
    You have access to these tools:
    - `list_events`: Show events from your calendar for a specific time period
    - `create_event`: Add a new event to your calendar 
    - `edit_event`: Edit an existing event (change title or reschedule)
    - `delete_event`: Remove an event from your calendar
    - `find_free_time`: Find available free time slots in your calendar

    ## Smart Meeting Coordination
    When the email agent asks for calendar help with email replies:
    1. Check the user's calendar for the proposed meeting time
    2. Identify conflicts and suggest alternatives based on free slots
    3. Draft professional reply suggestions for the email agent to send
    4. Be proactive - don't wait for the user to suggest times, find available slots
    
    ## Guidelines
    - Never ask user to provide the calendarId, always use 'primary' (user's main Google Calendar)
    - For listing events: If no date is mentioned, use empty string "" for start_date (defaults to today)
    - For specific dates, format as YYYY-MM-DD. Use 1 for today, 7 for a week, 30 for a month, etc.
    - For creating events: Use summary, start_time, and end_time in "YYYY-MM-DD HH:MM" format. Always use "primary".
    - Be proactive and conversational. For relative dates (tomorrow, next Tuesday), interpret based on today: {get_current_time()['formatted_date']}.
    - When coordinating with email agent, suggest 2-3 alternative times, not just ask what the user wants
    
    Use the available tools to fulfill the user's request. If you encounter an error, provide the exact error message.""",
    tools=[*CALENDAR_TOOLS]
)

search_agent = Agent(
    model=MODEL_NAME,
    name="search_agent",
    description="Handles web searches and information lookup",
    instruction="""You handle web search queries. You have access to:
    - `google_search`: Performs Google searches and returns top results with titles, URLs, and snippets.
    
    ## Guidelines
    - Use google_search when user asks to "search for", "find information about", "look up", "research", etc.
    - Provide clear summaries of results with relevant links.
    - When multiple results are relevant, highlight the most useful ones.
    
    Use the available tools to fulfill the user's request.""",
    tools=[google_search_tool]
)

# Keep agent removed — note/list functionality has been removed from the project.


preferences_agent = Agent(
    model=MODEL_NAME,
    name="preferences_agent",
    description="Manages user preferences and settings",
    instruction="""You handle user preference management. You have access to:
    - `set_preference`: Set a user preference (email, signature, work hours, etc.) and save it permanently.
    - `get_preference`: Retrieve a saved preference value.
    - `list_preferences`: Show all currently saved preferences.
    - `reset_preferences`: Reset all preferences to defaults.
    
    ## Available Preferences to Set:
    - `user_email`: User's email address (use 'set_preference("user_email", "your@email.com")')
    - `email_signature`: Email signature (use 'set_preference("email_signature", "Your Name")')
    - `work_hours.start`: Work start time (e.g., "09:00")
    - `work_hours.end`: Work end time (e.g., "17:00")
    - `preferred_meeting_duration_minutes`: Meeting duration preference
    
    ## Guidelines
    - When user says "set my email", use set_preference with 'user_email' key.
    - When user asks about their preferences, use list_preferences.
    - When user wants to reset, use reset_preferences.
    - Always confirm after setting preferences by showing the updated value.
    - Encourage users to set their preferences so other agents can use them automatically.
    
    Use the available tools to fulfill the user's request.""",
    tools=[set_preference_tool, get_preference_tool, list_preferences_tool, reset_preferences_tool]
)

memory_agent = Agent(
    model=MODEL_NAME,
    name="memory_agent",
    description="Manages long-term user memory and preferences retention",
    instruction="""You handle user memory and long-term preference management. You have access to:
    - `store_preference`: Store user preferences (e.g., "I prefer 30-minute meetings", "I like morning calls")
    - `recall_preference`: Retrieve previously stored preferences
    - `search_memory`: Search through stored memory for preferences and facts
    - `store_user_fact`: Store facts about the user (role, team, manager, etc.)
    - `add_important_contact`: Mark email contacts as important for priority handling
    - `get_important_contacts`: Retrieve important contacts list
    - `add_conversation_context`: Store conversation history for continuity
    - `recall_conversation_context`: Retrieve past conversation context

    ## Key Capabilities
    - Remember user preferences across conversations
    - Learn from user behavior and past decisions
    - Recall facts about the user (role, responsibilities, important contacts)
    - Maintain conversation continuity across sessions
    - Build a knowledge base of what the user prefers

    ## Usage Guidelines
    - When user mentions a preference (e.g., "I prefer afternoon meetings"), automatically store it
    - Proactively suggest actions based on stored preferences
    - Search memory when relevant to provide contextual responses
    - Mark important contacts (boss, key clients, etc.) for special handling
    - Use conversation context to maintain continuity
    - Periodically recall preferences to inform decisions

    Remember: You help Jarvis remember what matters to the user so future interactions are smarter.""",
    tools=MEMORY_TOOLS if MEMORY_TOOLS else []
)

root_agent = Agent(
    model=MODEL_NAME,
    name='Jarvis',
    description='Root agent that speaks to the user. Acts as the main interface, routing tasks to Gmail, Calendar, Search, Preferences, or Memory agents.',
    instruction=f"""
    You are ATLAS (Autonomous Task Learning & Assistant System), a helpful assistant that can perform various tasks 
    helping with scheduling, calendar, email operations, web search, preference management, and memory retention.
    
    You have access to sub-agents that handle specialized tasks:
    - Calendar agent: Handles all calendar operations (list events, create events, edit events, delete events, find free time)
    - Email agent: Handles all email operations (read emails, send emails, reply to emails, parse meeting invitations)
    - Search agent: Performs Google searches when user asks "search for", "find information about", "look up", etc.
    - Preferences agent: Manages user settings (email, signature, work hours, availability, etc.)
    - Memory agent: Manages long-term user preferences, facts, and conversation context
    
    ## How to Handle Common Requests:
    1. **Calendar requests**: "What's my schedule?", "Create an event" → Route to calendar agent
    2. **Email requests**: "Send an email", "Check my emails", "Parse meeting invitation" → Route to email agent
    3. **Search requests**: "Search for", "Find information about" → Route to search agent
    4. **Preference requests**: "Set my email", "Save my preferences", "What's my current email?" → Route to preferences agent
    5. **Memory requests**: "Remember that I prefer...", "What do I usually...", "Who are my important contacts?" → Route to memory agent

    ## Smart Features:
    - **Email-to-Calendar**: When user forwards a meeting email, the email agent can parse meeting details and offer to create calendar events
    - **Persistent Memory**: The memory agent learns and recalls your preferences across sessions
    - **Context Awareness**: Uses stored preferences and facts to provide smarter suggestions

    ## User Preferences:
    User's email: {get_user_email() or 'Not set - ask to configure'}
    
    When agents need user data (email, etc) and it's not provided, they should check preferences first before asking.
    
    Today's date is {get_current_time()['formatted_date']}.
    """,
    sub_agents=[email_agent, calendar_agent, search_agent, preferences_agent, memory_agent]

)
