"""User Memory System

Persistent memory for storing user context, preferences, and conversation history.
Allows the agent to remember user preferences, past decisions, and important context.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


# Memory storage location
PROJECT_ROOT = Path(__file__).parent.parent.parent
MEMORY_FILE = PROJECT_ROOT / "user_memory.json"


def _ensure_memory_file():
    """Ensure memory file exists with default structure."""
    if not MEMORY_FILE.exists():
        default_memory = {
            "preferences_memory": {},  # Long-term user preferences
            "conversation_context": [],  # Recent conversation history
            "user_facts": {},  # Facts about the user (name, role, team, etc.)
            "meeting_patterns": [],  # Past meeting preferences
            "email_patterns": [],  # Email sending patterns
            "important_contacts": [],  # VIP/important email contacts
            "version": 1
        }
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MEMORY_FILE, 'w') as f:
            json.dump(default_memory, f, indent=2)
    return MEMORY_FILE


def load_memory() -> Dict[str, Any]:
    """Load all user memory."""
    try:
        _ensure_memory_file()
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading memory: {e}")
        return {
            "preferences_memory": {},
            "conversation_context": [],
            "user_facts": {},
            "meeting_patterns": [],
            "email_patterns": [],
            "important_contacts": [],
            "version": 1
        }


def save_memory(memory: Dict[str, Any]) -> bool:
    """Save user memory."""
    try:
        _ensure_memory_file()
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving memory: {e}")
        return False


def store_preference(key: str, value: Any, category: str = "general") -> Dict[str, Any]:
    """
    Store a user preference in memory.
    
    Args:
        key: Preference key (e.g., "meeting_duration", "email_style")
        value: Preference value
        category: Category for organizing preferences
    
    Returns:
        Result dict with success status
    """
    try:
        memory = load_memory()
        if category not in memory["preferences_memory"]:
            memory["preferences_memory"][category] = {}
        
        memory["preferences_memory"][category][key] = {
            "value": value,
            "stored_at": datetime.now().isoformat(),
            "category": category
        }
        
        save_memory(memory)
        return {
            "success": True,
            "message": f"Stored preference: {key} = {value}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def recall_preference(key: str, category: str = "general") -> Dict[str, Any]:
    """
    Recall a stored user preference.
    
    Args:
        key: Preference key
        category: Category to search in
    
    Returns:
        Dict with success status and value if found
    """
    try:
        memory = load_memory()
        
        if category in memory["preferences_memory"]:
            if key in memory["preferences_memory"][category]:
                pref = memory["preferences_memory"][category][key]
                return {
                    "success": True,
                    "found": True,
                    "value": pref.get("value"),
                    "stored_at": pref.get("stored_at")
                }
        
        return {
            "success": True,
            "found": False,
            "value": None,
            "message": f"No preference found for '{key}' in category '{category}'"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def search_memory(query: str) -> Dict[str, Any]:
    """
    Search user memory for a query string (searches all categories).
    
    Args:
        query: Search query (case-insensitive)
    
    Returns:
        Dict with matching preferences
    """
    try:
        memory = load_memory()
        results = []
        query_lower = query.lower()
        
        for category, prefs in memory["preferences_memory"].items():
            for key, pref_data in prefs.items():
                if query_lower in key.lower() or query_lower in str(pref_data.get("value", "")).lower():
                    results.append({
                        "key": key,
                        "category": category,
                        "value": pref_data.get("value"),
                        "stored_at": pref_data.get("stored_at")
                    })
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def store_user_fact(key: str, value: Any) -> Dict[str, Any]:
    """
    Store a fact about the user (name, role, team, etc.).
    
    Args:
        key: Fact key (e.g., "role", "team", "manager_email")
        value: Fact value
    
    Returns:
        Result dict
    """
    try:
        memory = load_memory()
        memory["user_facts"][key] = {
            "value": value,
            "stored_at": datetime.now().isoformat()
        }
        save_memory(memory)
        return {
            "success": True,
            "message": f"Stored fact: {key} = {value}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def recall_user_fact(key: str) -> Dict[str, Any]:
    """Recall a stored user fact."""
    try:
        memory = load_memory()
        if key in memory["user_facts"]:
            fact = memory["user_facts"][key]
            return {
                "success": True,
                "found": True,
                "value": fact.get("value")
            }
        return {
            "success": True,
            "found": False,
            "value": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def add_important_contact(email: str, name: str = "", relationship: str = "") -> Dict[str, Any]:
    """
    Mark a contact as important (for priority email handling).
    
    Args:
        email: Email address
        name: Contact name
        relationship: Relationship (e.g., "boss", "client", "colleague")
    
    Returns:
        Result dict
    """
    try:
        memory = load_memory()
        contact = {
            "email": email,
            "name": name,
            "relationship": relationship,
            "added_at": datetime.now().isoformat()
        }
        
        # Check if already exists
        if not any(c["email"] == email for c in memory["important_contacts"]):
            memory["important_contacts"].append(contact)
            save_memory(memory)
        
        return {
            "success": True,
            "message": f"Added important contact: {email}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_important_contacts() -> Dict[str, Any]:
    """Get all important contacts."""
    try:
        memory = load_memory()
        return {
            "success": True,
            "contacts": memory.get("important_contacts", []),
            "count": len(memory.get("important_contacts", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def add_conversation_context(role: str, content: str, topic: str = "general") -> Dict[str, Any]:
    """
    Add conversation context to memory for continuity.
    
    Args:
        role: "user" or "assistant"
        content: Message content
        topic: Topic/category of conversation
    
    Returns:
        Result dict
    """
    try:
        memory = load_memory()
        context = {
            "role": role,
            "content": content,
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        }
        
        # Keep only last 50 messages to avoid memory bloat
        memory["conversation_context"].append(context)
        if len(memory["conversation_context"]) > 50:
            memory["conversation_context"] = memory["conversation_context"][-50:]
        
        save_memory(memory)
        return {
            "success": True,
            "message": "Added conversation context"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def recall_conversation_context(topic: str = None, limit: int = 10) -> Dict[str, Any]:
    """
    Recall recent conversation context, optionally filtered by topic.
    
    Args:
        topic: Optional topic filter
        limit: Max number of messages to return
    
    Returns:
        List of recent conversations
    """
    try:
        memory = load_memory()
        context = memory.get("conversation_context", [])
        
        if topic:
            context = [c for c in context if c.get("topic") == topic]
        
        # Return most recent first
        context = context[-limit:]
        context.reverse()
        
        return {
            "success": True,
            "context": context,
            "count": len(context)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_all_preferences() -> Dict[str, Any]:
    """Get all stored preferences organized by category."""
    try:
        memory = load_memory()
        return {
            "success": True,
            "preferences": memory.get("preferences_memory", {}),
            "user_facts": memory.get("user_facts", {}),
            "important_contacts_count": len(memory.get("important_contacts", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def reset_memory() -> Dict[str, Any]:
    """Reset all user memory to defaults."""
    try:
        default_memory = {
            "preferences_memory": {},
            "conversation_context": [],
            "user_facts": {},
            "meeting_patterns": [],
            "email_patterns": [],
            "important_contacts": [],
            "version": 1
        }
        save_memory(default_memory)
        return {
            "success": True,
            "message": "User memory reset to defaults"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# FunctionTool wrappers for ADK
try:
    from google.adk.tools import FunctionTool
    
    store_preference_tool = FunctionTool(
        func=store_preference,
        description="Store a user preference in long-term memory. Use this to remember user preferences like 'I prefer 30-minute meetings' or 'I like morning calls'."
    )
    
    recall_preference_tool = FunctionTool(
        func=recall_preference,
        description="Recall a previously stored user preference from memory."
    )
    
    search_memory_tool = FunctionTool(
        func=search_memory,
        description="Search user memory for preferences and facts. Use keywords to find stored information about the user."
    )
    
    store_user_fact_tool = FunctionTool(
        func=store_user_fact,
        description="Store a fact about the user (e.g., role, team, manager). Use this to remember personal and professional information."
    )
    
    add_important_contact_tool = FunctionTool(
        func=add_important_contact,
        description="Mark a contact as important for priority email handling."
    )
    
    get_important_contacts_tool = FunctionTool(
        func=get_important_contacts,
        description="Retrieve list of marked important contacts."
    )
    
    add_conversation_context_tool = FunctionTool(
        func=add_conversation_context,
        description="Store conversation context in memory for continuity across sessions."
    )
    
    recall_conversation_context_tool = FunctionTool(
        func=recall_conversation_context,
        description="Retrieve recent conversation context from memory."
    )
    
    MEMORY_TOOLS = [
        store_preference_tool,
        recall_preference_tool,
        search_memory_tool,
        store_user_fact_tool,
        add_important_contact_tool,
        get_important_contacts_tool,
        add_conversation_context_tool,
        recall_conversation_context_tool,
    ]
    
except Exception:
    MEMORY_TOOLS = []
