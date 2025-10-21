import difflib
from typing import List, Tuple
from contact import Contact
from trie import search_firstname_prefix, search_lastname_prefix, search_phone_prefix
from popularity_graph import get_popularity_score
from data_load import normalize_phone
import data


def search_by_firstname(prefix: str, exact_match: bool = False) -> List[Tuple[Contact, float]]:

    if not prefix:
        return []
    
    # Trie search returns [(key, contact_list), ...]
    results = search_firstname_prefix(prefix)
    
    # Flatten: collect all contacts from all matching keys
    contacts_with_scores = []
    for key, contact_list in results:
        if exact_match and key.lower() != prefix.lower():
            continue
        for contact in contact_list:
            score = get_popularity_score(contact.phone)
            contacts_with_scores.append((contact, score))
    
    contacts_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    return contacts_with_scores


def search_by_lastname(prefix: str, exact_match: bool = False) -> List[Tuple[Contact, float]]:

    if not prefix:
        return []
    

    results = search_lastname_prefix(prefix)
    
    contacts_with_scores = []
    for key, contact_list in results:
        if exact_match and key.lower() != prefix.lower():
            continue
        for contact in contact_list:
            score = get_popularity_score(contact.phone)
            contacts_with_scores.append((contact, score))
    
    contacts_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    return contacts_with_scores


def search_by_phone(prefix: str) -> List[Tuple[Contact, float]]:

    try:
        normalized_prefix = normalize_phone(prefix)
    except ValueError:
        return []
    
    results = search_phone_prefix(normalized_prefix)
    
    contacts_with_scores = []
    for _, contact_list in results:
        for contact in contact_list:
            score = get_popularity_score(contact.phone)
            contacts_with_scores.append((contact, score))
    
    contacts_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    return contacts_with_scores


def autocomplete_names(prefix: str, is_firstname: bool = True) -> List[Tuple[str, int, float]]:

    if not prefix:
        return []
    

    if is_firstname:
        results = search_firstname_prefix(prefix)
    else:
        results = search_lastname_prefix(prefix)
    
    name_stats = []
    for complete_name, contact_list in results:
        contact_count = len(contact_list)
        total_popularity = sum(get_popularity_score(c.phone) for c in contact_list)
        name_stats.append((complete_name, contact_count, total_popularity))
    
    name_stats.sort(key=lambda x: x[2], reverse=True)
    return name_stats[:4]


def did_you_mean_phone(phone_input: str) -> List[Tuple[str, Contact, float]]:
    try:
        normalized_input = normalize_phone(phone_input)
    except ValueError:
        return []
    
    all_phones = list(data.phonebook.keys())
    
    close_matches = difflib.get_close_matches(normalized_input, all_phones, n=10, cutoff=0.6)
    
    if not close_matches:
        return []
    
    suggestions = []
    for phone in close_matches:
        contact = data.phonebook[phone]
        score = get_popularity_score(phone)
        suggestions.append((phone, contact, score))
    
    suggestions.sort(key=lambda x: x[2], reverse=True)
    return suggestions[:4]


def format_search_results(results: List[Tuple[Contact, float]], page_size: int = 15) -> None:

    if not results:
        print("No results found matching your search.")
        return
    
    total = len(results)
    shown = 0
    
    while shown < total:
        batch = results[shown:shown + page_size]
        for rank, (contact, score) in enumerate(batch, start=shown + 1):
            print(f"{rank}. {contact.first_name} {contact.last_name}: {contact.phone} (popularity: {score:.2f})")
        
        shown += len(batch)
        
        if shown < total:
            response = input(f"\nShowing {shown} of {total} results. Show more? (y/n): ").strip().lower()
            if response != 'y':
                break
        else:
            print(f"\nShowing all {total} results.")


def prompt_and_search():

    print("\nSearch Phone Book")
    print("1. Search by first name")
    print("2. Search by last name")
    print("3. Search by phone number")
    
    choice = input("Select search type (1-3): ").strip()
    
    if choice == "1":
        while True:
            prefix = input("Enter first name prefix: ").strip()
            if not prefix:
                print("Empty input.")
                continue
            break

        use_exact_match = False
        suggestions = autocomplete_names(prefix, is_firstname=True)
        if suggestions:
            print("\nAutocomplete suggestions:")
            for i, (name, count, popularity) in enumerate(suggestions, start=1):
                print(f"{i}. {name} ({count} contacts, total popularity: {popularity:.2f})")
            
            choice_input = input("\nSelect option (1-4) or press Enter to search with your input: ").strip()
            if choice_input in ['1', '2', '3', '4']:
                idx = int(choice_input) - 1
                if 0 <= idx < len(suggestions):
                    prefix = suggestions[idx][0]
                    use_exact_match = True
                    print(f"Searching for exact name: {prefix}")
        
        results = search_by_firstname(prefix, exact_match=use_exact_match)
        print(f"\nSearch results for first name '{prefix}':")
        format_search_results(results)
    
    elif choice == "2":
        while True:
            prefix = input("Enter last name prefix: ").strip()
            if not prefix:
                print("Empty input.")
                continue
            break
        
        use_exact_match = False
        suggestions = autocomplete_names(prefix, is_firstname=False)
        if suggestions:
            print("\nAutocomplete suggestions:")
            for i, (name, count, popularity) in enumerate(suggestions, start=1):
                print(f"{i}. {name} ({count} contacts, total popularity: {popularity:.2f})")
            
            choice_input = input("\nSelect option (1-4) or press Enter to search with your input: ").strip()
            if choice_input in ['1', '2', '3', '4']:
                idx = int(choice_input) - 1
                if 0 <= idx < len(suggestions):
                    prefix = suggestions[idx][0]
                    use_exact_match = True
                    print(f"Searching for exact name: {prefix}")
        
        results = search_by_lastname(prefix, exact_match=use_exact_match)
        print(f"\nSearch results for last name '{prefix}':")
        format_search_results(results)
    
    elif choice == "3":
        while True:
            prefix = input("Enter phone number: ").strip()
            if not prefix:
                print("Empty input.")
                continue
            break
        
        results = search_by_phone(prefix)
        
        if not results:
            print(f"\nNo results found for '{prefix}'.")
            suggestions = did_you_mean_phone(prefix)
            
            if suggestions:
                print("\nDid you mean:")
                for i, (phone, contact, score) in enumerate(suggestions, start=1):
                    print(f"{i}. {phone} ({contact.first_name} {contact.last_name}, popularity: {score:.2f})")
                
                choice_input = input("\nSelect a number (1-4) or press Enter to cancel: ").strip()
                if choice_input in ['1', '2', '3', '4']:
                    idx = int(choice_input) - 1
                    if 0 <= idx < len(suggestions):
                        selected_phone = suggestions[idx][0]
                        # Search with the selected phone
                        results = search_by_phone(selected_phone)
                        print(f"\nSearch results for phone '{selected_phone}':")
                        format_search_results(results)
            else:
                print("No similar phone numbers found.")
        else:
            print(f"\nSearch results for phone '{prefix}':")
            format_search_results(results)
    
    else:
        print("Invalid choice. Returning to main menu.")
