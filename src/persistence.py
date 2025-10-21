import os
import pickle
import data


PREPROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'preprocessed')


def ensure_preprocessed_dir():
    os.makedirs(PREPROCESSED_DIR, exist_ok=True)


def preprocessed_files_exist():
    required_files = [
        'phonebook.pickle',
        'calls.pickle',
        'call_index.pickle',
        'tries.pickle',
        'popularity_graph.pickle',
        'blocked.pickle'
    ]
    return all(os.path.exists(os.path.join(PREPROCESSED_DIR, f)) for f in required_files)


def save_preprocessed():

    ensure_preprocessed_dir()
    
    print("Saving preprocessed data...")
    

    with open(os.path.join(PREPROCESSED_DIR, 'phonebook.pickle'), 'wb') as f:
        pickle.dump(data.phonebook, f)
    print("  Saved phonebook.pickle")
    

    with open(os.path.join(PREPROCESSED_DIR, 'calls.pickle'), 'wb') as f:
        pickle.dump(data.calls, f)
    print("  Saved calls.pickle")

    with open(os.path.join(PREPROCESSED_DIR, 'call_index.pickle'), 'wb') as f:
        pickle.dump(data.call_index, f)
    print("  Saved call_index.pickle")

    tries = {
        'firstname': data.firstname_trie,
        'lastname': data.lastname_trie,
        'phone': data.phone_trie
    }
    with open(os.path.join(PREPROCESSED_DIR, 'tries.pickle'), 'wb') as f:
        pickle.dump(tries, f)
    print("  Saved tries.pickle")
    

    with open(os.path.join(PREPROCESSED_DIR, 'popularity_graph.pickle'), 'wb') as f:
        pickle.dump(data.popularity_graph, f)
    print("  Saved popularity_graph.pickle")
    
    with open(os.path.join(PREPROCESSED_DIR, 'blocked.pickle'), 'wb') as f:
        pickle.dump(data.blocked, f)
    print("  Saved blocked.pickle")
    
    print("Preprocessed data saved successfully.")


def load_preprocessed():

    if not preprocessed_files_exist():
        print("Preprocessed files not found.")
        return False
    
    print("Loading preprocessed data...")
    
    try:

        with open(os.path.join(PREPROCESSED_DIR, 'phonebook.pickle'), 'rb') as f:
            data.phonebook = pickle.load(f)
        print(f"  Loaded {len(data.phonebook)} contacts")
        

        with open(os.path.join(PREPROCESSED_DIR, 'calls.pickle'), 'rb') as f:
            data.calls = pickle.load(f)
        print(f"  Loaded {len(data.calls)} calls")
        

        with open(os.path.join(PREPROCESSED_DIR, 'call_index.pickle'), 'rb') as f:
            data.call_index = pickle.load(f)
        print(f"  Loaded call index with {len(data.call_index)} numbers")
        

        with open(os.path.join(PREPROCESSED_DIR, 'tries.pickle'), 'rb') as f:
            tries = pickle.load(f)
            data.firstname_trie = tries['firstname']
            data.lastname_trie = tries['lastname']
            data.phone_trie = tries['phone']
        print("  Loaded tries")
        

        with open(os.path.join(PREPROCESSED_DIR, 'popularity_graph.pickle'), 'rb') as f:
            data.popularity_graph = pickle.load(f)
        print(f"  Loaded popularity graph with {len(data.popularity_graph.nodes)} nodes")
        

        with open(os.path.join(PREPROCESSED_DIR, 'blocked.pickle'), 'rb') as f:
            data.blocked = pickle.load(f)
        print(f"  Loaded {len(data.blocked)} blocked numbers")
        
        print("Preprocessed data loaded successfully.")
        return True
    
    except Exception as e:
        print(f"Error loading preprocessed data: {e}")
        return False
