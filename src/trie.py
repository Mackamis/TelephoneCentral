import data

def insert_firstname(name, contact):
    key = name.lower()
    if key not in data.firstname_trie:
        data.firstname_trie[key] = []
    data.firstname_trie[key].append(contact)

def insert_lastname(name, contact):
    key = name.lower()
    if key not in data.lastname_trie:
        data.lastname_trie[key] = []
    data.lastname_trie[key].append(contact)

def insert_phone(phone, contact):
    key = phone
    if key not in data.phone_trie:
        data.phone_trie[key] = []
    data.phone_trie[key].append(contact)

def search_firstname_prefix(prefix):
    return list(data.firstname_trie.items(prefix=prefix.lower()))

def search_lastname_prefix(prefix):
    return list(data.lastname_trie.items(prefix=prefix.lower()))

def search_phone_prefix(prefix):
    return list(data.phone_trie.items(prefix=prefix))
