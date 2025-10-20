import pytrie

firstname_trie = pytrie.StringTrie()
lastname_trie = pytrie.StringTrie()
phone_trie = pytrie.StringTrie()

def insert_firstname(name, contact):
    key = name.lower()
    firstname_trie[key] = contact

def insert_lastname(name, contact):
    key = name.lower()
    lastname_trie[key] = contact

def insert_phone(phone, contact):
    key = phone
    phone_trie[key] = contact

def search_firstname_prefix(prefix):
    return list(firstname_trie.items(prefix=prefix.lower()))

def search_lastname_prefix(prefix):
    return list(lastname_trie.items(prefix=prefix.lower()))

def search_phone_prefix(prefix):
    return list(phone_trie.items(prefix=prefix))
