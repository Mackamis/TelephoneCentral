# Centralized global data structures for the telephone central project

# Phonebook: number -> Contact
phonebook = None
# List of all calls
calls = None
# Set of blocked numbers
blocked = None
# Call index: number -> List[Call]
call_index = None

# Popularity graph (networkx DiGraph)
popularity_graph = None

# Tries for fast prefix search
from trie import firstname_trie, lastname_trie, phone_trie

def init_popularity_graph(graph):
	global popularity_graph
	popularity_graph = graph
