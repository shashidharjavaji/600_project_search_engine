# src/trie.py



class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.occurrence_list_index = None  # Index to external occurrence list

class OccurrenceList:
    def __init__(self):
        self.documents = {}  # {doc_id: [positions]}
        
    def add_occurrence(self, doc_id, position):
        if doc_id not in self.documents:
            self.documents[doc_id] = []
        self.documents[doc_id].append(position)
        # Keep positions sorted
        self.documents[doc_id].sort()

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.occurrence_lists = []  # External storage for occurrence lists
    
    def insert(self, word, doc_id, position):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        if not node.is_end_of_word:
            node.is_end_of_word = True
            node.occurrence_list_index = len(self.occurrence_lists)
            self.occurrence_lists.append(OccurrenceList())
            
        self.occurrence_lists[node.occurrence_list_index].add_occurrence(doc_id, position)

    def _find_node(self, word):
        """
        Helper method to find the node for a given word
        Returns None if word not found
        """
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return None
            node = node.children[char]
        return node if node.is_end_of_word else None

    def search(self, word):
        """
        Search for a word in the trie
        Returns (is_found, occurrence_list_index) tuple
        """
        node = self._find_node(word)
        if node:
            return True, node.occurrence_list_index
        return False, None

    def intersection_search(self, query_terms):
        """
        Find documents containing all query terms
        """
        if not query_terms:
            return set()
            
        # Get occurrence lists for all terms
        occurrences = []
        for term in query_terms:
            node = self._find_node(term)
            if not node or not node.is_end_of_word:
                return set()  # Term not found
            occurrences.append(
                self.occurrence_lists[node.occurrence_list_index].documents.keys()
            )
            
        # Find intersection of all document sets
        result = set.intersection(*map(set, occurrences))
        return result

    def get_occurrence_list(self, word):
        """
        Get the occurrence list for a word
        """
        node = self._find_node(word)
        if node and node.occurrence_list_index is not None:
            return self.occurrence_lists[node.occurrence_list_index]
        return None