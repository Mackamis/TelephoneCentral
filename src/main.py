import sys
import atexit
from data_load import load_all_data
import data
from call_from_file import call_from_file
from history import (
    prompt_and_show_history_for,
    prompt_and_show_history_between,
)
from live_call import prompt_and_start_live_call
from search import prompt_and_search
from persistence import load_preprocessed, save_preprocessed, preprocessed_files_exist
from simulator import run_overload_simulation

_save_done = False

def save_on_exit():
    global _save_done
    if not _save_done and data.phonebook is not None:
        save_preprocessed()
        _save_done = True

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

def run_overload_action():
    run_overload_simulation(1000)

def exit_action():
    save_on_exit()
    print("Exiting.")
    sys.exit(0)

def main():
    print("Telephone Central CLI")
    
    atexit.register(save_on_exit)
    
    if preprocessed_files_exist():
        print("\nPreprocessed data found.")
        print("1. Load preprocessed data (fast)")
        print("2. Rebuild from source files (slow)")
        
        while True:
            choice = input("\nSelect option (1-2): ").strip()
            if choice == "1":
                if load_preprocessed():
                    print("Data loaded successfully.")
                    break
                else:
                    print("Failed to load preprocessed data. Rebuilding from source...")
                    choice = "2"
            
            if choice == "2":
                try:
                    load_all_data(
                        '../data/phones.txt',
                        '../data/calls.txt',
                        '../data/blocked.txt'
                    )
                    print("Data loaded successfully.")
                    break
                except Exception as e:
                    print(f"Error loading data: {e}")
                    sys.exit(1)
            else:
                print("Invalid choice. Please select 1 or 2.")
    else:
        print("\nNo preprocessed data found. Building from source files...")
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
        "5": prompt_and_show_history_for,
        "6": prompt_and_show_history_between,
        "7": prompt_and_start_live_call,
        "8": prompt_and_search,
        "9": run_overload_action,
    }
    menu_text = [
        "1. Show contacts",
        "2. Show calls",
        "3. Show blocked numbers",
        "4. Simulate calls from file",
        "5. Show history for a number",
        "6. Show history between two numbers",
        "7. Start a live call",
        "8. Search phone book",
        "9. Run overload simulation (1000 calls)",
        "Press Enter to exit",
    ]
    while True:
        print("\nMenu:")
        for line in menu_text:
            print(line)
        choice = input("Select option: ").strip()
        
        if not choice:
            exit_action()
        
        action = menu.get(choice)
        if action:
            action()
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
