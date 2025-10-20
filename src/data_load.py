from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
from call import Call
from contact import Contact
from trie import insert_firstname, insert_lastname, insert_phone
import data

class PhoneNormalizationError(Exception):
    pass


def normalize_phone(phone):
    normalized = phone.replace(' ', '').replace('-', '')
    
    if not normalized:
        raise ValueError(f"Phone number '{phone}' is empty after normalization")
    
    if not normalized.isdigit():
        raise ValueError(f"Phone number '{phone}' contains non-digit characters after normalization: '{normalized}'")
    
    return normalized


def parse_phone_line(line: str) -> Optional[Tuple[str, str, str]]:
    line = line.strip()

    if not line or line.startswith('#'):
        return None
    
    name_part, phone_part = line.split(',', 1)
    name_part = name_part.strip()
    phone_part = phone_part.strip()

    name_parts = name_part.split()
    if len(name_parts) < 2:
        raise ValueError(f"Invalid name in phone line: '{name_part}'")

    firstname = name_parts[0]
    lastname = name_parts[1]
    phone = phone_part
    
    normalized_phone = normalize_phone(phone)
    
    return firstname, lastname, normalized_phone


def parse_call_line(line: str) -> Optional[Tuple[str, str, datetime, str]]:

    line = line.strip()

    if not line or line.startswith('#'):
        return None

    parts = [p.strip() for p in line.split(',')]

    if len(parts) != 4:
        raise ValueError(f"Invalid call line format (expected 4 comma-separated fields): '{line}'")

    caller_raw, callee_raw, timestamp_str, duration_str = parts

    try:
        caller_normalized = normalize_phone(caller_raw)
    except ValueError as e:
        raise PhoneNormalizationError(f"Caller normalization failed: {e}")

    try:
        callee_normalized = normalize_phone(callee_raw)
    except ValueError as e:
        raise PhoneNormalizationError(f"Callee normalization failed: {e}")

    try:
        timestamp = datetime.strptime(timestamp_str, "%d.%m.%Y %H:%M:%S")
    except Exception:
        raise ValueError(f"Invalid timestamp format '{timestamp_str}'; expected 'DD.MM.YYYY HH:MM:SS'")

    dur = duration_str.strip()
    parts_d = dur.split(':')
    if len(parts_d) == 3:
        try:
            h, m, s = parts_d
            duration_secs = int(h) * 3600 + int(m) * 60 + int(s)
        except Exception:
            raise ValueError(f"Invalid duration '{duration_str}'; expected HH:MM:SS with numeric fields")
    else:
        raise ValueError(f"Invalid duration '{duration_str}'; expected HH:MM:SS")

    if duration_secs < 0:
        raise ValueError(f"Duration cannot be negative: {duration_secs}")

    return caller_normalized, callee_normalized, timestamp, duration_secs


def parse_blocked_line(line: str) -> Optional[str]:

    line = line.strip()
    
    if not line or line.startswith('#'):
        return None
    
    normalized_phone = normalize_phone(line)
    
    return normalized_phone


def load_phones(filepath):
    data.phonebook = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            try:
                result = parse_phone_line(line)
                if result is None:
                    continue  # Skip 
                firstname, lastname, phone = result
                # Check for duplicate phone numbers
                if phone in data.phonebook:
                    print(f"Warning: Duplicate phone number '{phone}' at line {line_num}. Keeping first occurrence.")
                    continue
                contact = Contact(phone, firstname, lastname)
                data.phonebook[phone] = contact
                # Insert into tries
                insert_firstname(firstname, contact)
                insert_lastname(lastname, contact)
                insert_phone(phone, contact)
            except ValueError as e:
                # Skip invalid lines
                print(f"Warning: Skipping invalid phones.txt line {line_num}: {e}")


def load_calls(filepath):
    data.calls = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            try:
                result = parse_call_line(line)
                if result is None:
                    continue  # Skip
                caller, callee, timestamp, duration_secs = result
                call = Call(caller, callee, timestamp, duration_secs)
                data.calls.append(call)
            except PhoneNormalizationError as e:
                print(f"Warning: Skipping calls.txt line {line_num} due to phone normalization error: {e}")
                continue
            except ValueError as e:
                print(f"Warning: Skipping calls.txt line {line_num} due to parse error: {e}")
                continue


def load_blocked(filepath):
    data.blocked = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            try:
                result = parse_blocked_line(line)
                if result is None:
                    continue  # Skip
                data.blocked.add(result)
            except ValueError as e:
                raise ValueError(f"Error parsing blocked.txt at line {line_num}: {e}")


def load_all_data(phones_path, calls_path, blocked_path):
    print("Loading phone book...")
    load_phones(phones_path)
    print(f"  Loaded {len(data.phonebook)} contacts")
    print("Loading call history...")
    load_calls(calls_path)
    print(f"  Loaded {len(data.calls)} calls")
    print("Loading blocked numbers...")
    load_blocked(blocked_path)
    print(f"  Loaded {len(data.blocked)} blocked numbers")
    data.calls.sort(key=lambda c: c.start)
    print("  Sorted global call list by start time")
    print("Building popularity graph from calls.txt...")
    from popularity_graph import rebuild_from_calls
    rebuild_from_calls(data.calls, None)
    print(f"  Popularity graph has {len(data.popularity_graph.nodes)} nodes")
    print("Building call index...")
    from index import build_call_index
    data.call_index = build_call_index(data.calls)
    print(f"  Indexed {len(data.call_index)} phone numbers with call history")


if __name__ == "__main__":
    # Test the data loading functions
    load_all_data(
        '../data/phones.txt',
        '../data/calls.txt', 
        '../data/blocked.txt'
    )
    
    print("\n=== Summary ===")
    print(f"Total contacts: {len(data.phonebook)}")
    print(f"Total calls: {len(data.calls)}")
    print(f"Total blocked: {len(data.blocked)}")
    print(f"Total indexed numbers: {len(data.call_index)}")
    
    # Samples
    if data.phonebook:
        print("\nSample contacts:")
        for phone, contact in list(data.phonebook.items())[:3]:
            print(f"  {contact.first_name} {contact.last_name}: {phone}")

    if data.calls:
        print("\nSample calls:")
        for call in data.calls[:3]:
            print(f"  {call.caller} → {call.callee} at {call.start} ({call.format_duration()})")

    if data.blocked:
        print("\nSample blocked numbers:")
        for i, phone in enumerate(list(data.blocked)[:3]):
            print(f"  {phone}")

    from index import get_calls_for_number
    if data.phonebook:
        sample_number = next(iter(data.phonebook.keys()))
        calls_for_sample = get_calls_for_number(data.call_index, sample_number)
        print(f"\nCall history for {sample_number} ({data.phonebook[sample_number].first_name}):")
        for call in calls_for_sample[:3]:
            print(f"  {call.caller} → {call.callee} at {call.start} ({call.format_duration()})")

