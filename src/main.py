import sys
from data_load import load_all_data
import data
from call_from_file import call_from_file
from history import (
    get_history_for,
    get_history_between,
    format_call,
    prompt_and_show_history_for,
    prompt_and_show_history_between,
)
from live_call import prompt_and_start_live_call

def print_contacts():
    print("\nContacts:")
    for phone, contact in data.phonebook.items():
        print(f"  {contact.first_name} {contact.last_name}: {phone}")

def print_calls():
    print("\nCalls:")
    for call in data.calls:
        print(f"  {call.caller} → {call.callee} at {call.start} ({call.format_duration()})")

def print_blocked():
    print("\nBlocked numbers:")
    for phone in data.blocked:
        print(f"  {phone}")

def simulate_calls_action():
    print("\nSimulating calls from call_simulation.txt...")
    call_from_file('../data/call_simulation.txt', data.blocked)

def exit_action():
    print("Exiting.")
    sys.exit(0)

def main():
    print("Telephone Central CLI")
    try:
        load_all_data(
            '../data/phones.txt',
            '../data/calls.txt',
            '../data/blocked.txt'
        )
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)
    menu = {
        "1": print_contacts,
        "2": print_calls,
        "3": print_blocked,
        "4": simulate_calls_action,
        "5": exit_action,
        "6": prompt_and_show_history_for,
        "7": prompt_and_show_history_between,
        "8": prompt_and_start_live_call,
    }
    menu_text = [
        "1. Show contacts",
        "2. Show calls",
        "3. Show blocked numbers",
        "4. Simulate calls from file",
        "5. Exit",
        "6. Show history for a number",
        "7. Show history between two numbers",
        "8. Start a live call",
    ]
    while True:
        print("\nMenu:")
        for line in menu_text:
            print(line)
        choice = input("Select option: ").strip()
        action = menu.get(choice)
        if action:
            action()
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
