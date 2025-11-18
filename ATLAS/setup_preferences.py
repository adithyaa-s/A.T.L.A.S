"""
Initialize and manage JARVIS preferences.
This script helps you set up your preferences for the JARVIS agent.
"""

from tools.preferences import (
    load_preferences,
    save_preferences,
    get_default_preferences,
)


def interactive_setup():
    """Interactive setup wizard for user preferences."""
    print("=" * 60)
    print("JARVIS Preferences Setup")
    print("=" * 60)
    
    prefs = get_default_preferences()
    
    # Email
    email = input("\nEnter your email address: ").strip()
    if email:
        prefs["user_email"] = email
    
    # Email signature
    print("\nEnter your email signature (press Enter for default):")
    signature = input(">> ").strip()
    if signature:
        prefs["email_signature"] = signature
    
    # Work hours
    print("\nEnter your work start time (HH:MM, default 09:00):")
    start = input(">> ").strip() or "09:00"
    prefs["work_hours"]["start"] = start
    
    print("Enter your work end time (HH:MM, default 17:00):")
    end = input(">> ").strip() or "17:00"
    prefs["work_hours"]["end"] = end
    
    # Availability
    print("\nDays you're typically available (y/n):")
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for day in days:
        response = input(f"  {day.capitalize()}? (y/n, default=weekday): ").strip().lower()
        if day in ["saturday", "sunday"]:
            prefs["availability"][day] = response == "y"
        else:
            prefs["availability"][day] = response != "n"
    
    # Save preferences
    if save_preferences(prefs):
        print("\n✓ Preferences saved successfully!")
        print("\nYour preferences:")
        print(f"  Email: {prefs['user_email']}")
        print(f"  Work hours: {prefs['work_hours']['start']} - {prefs['work_hours']['end']}")
        print(f"  Signature: {prefs['email_signature'][:50]}...")
    else:
        print("\n✗ Error saving preferences")


def show_preferences():
    """Show current preferences."""
    prefs = load_preferences()
    print("\n" + "=" * 60)
    print("Current Preferences")
    print("=" * 60)
    
    def print_dict(d, indent=0):
        for key, value in d.items():
            prefix = "  " * indent
            if isinstance(value, dict):
                print(f"{prefix}{key}:")
                print_dict(value, indent + 1)
            else:
                print(f"{prefix}{key}: {value}")
    
    print_dict(prefs)


def reset_preferences():
    """Reset preferences to defaults."""
    response = input("\nAre you sure you want to reset all preferences? (y/n): ").strip().lower()
    if response == "y":
        prefs = get_default_preferences()
        if save_preferences(prefs):
            print("✓ Preferences reset to defaults")
        else:
            print("✗ Error resetting preferences")
    else:
        print("Reset cancelled")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "setup":
            interactive_setup()
        elif command == "show":
            show_preferences()
        elif command == "reset":
            reset_preferences()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python setup_preferences.py [setup|show|reset]")
    else:
        print("JARVIS Preferences Manager")
        print("Usage:")
        print("  python setup_preferences.py setup  - Interactive setup wizard")
        print("  python setup_preferences.py show   - Show current preferences")
        print("  python setup_preferences.py reset  - Reset to defaults")
