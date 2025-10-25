import pytrie


phonebook = None

calls = None

blocked = None

call_index = None


popularity_graph = None

firstname_trie = pytrie.StringTrie()
lastname_trie = pytrie.StringTrie()
phone_trie = pytrie.StringTrie()


def init_popularity_graph(graph):
    global popularity_graph
    popularity_graph = graph
