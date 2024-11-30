# src/searcher.py

from src.text_processor import TextProcessor

class SearchEngine:
    def __init__(self, trie, documents):
        self.trie = trie
        self.documents = documents
        self.processor = TextProcessor()
    
    def search(self, query):
        """
        Search for documents containing all query terms
        """
        # Process query
        query_terms = self.processor.process_query(query)
        
        if not query_terms:
            return []
        
        # Find documents containing all terms
        matching_docs = self.trie.intersection_search(query_terms)
        
        if not matching_docs:
            return []
            
        # Rank matching documents
        ranked_results = self._rank_documents(matching_docs, query_terms)
        return ranked_results
    
    def _rank_documents(self, matching_docs, query_terms):
        """
        Rank documents based on term frequency and position
        """
        scores = {}
        for doc_id in matching_docs:
            score = 0
            for term in query_terms:
                # Get occurrence list
                occurrence_list = self.trie.get_occurrence_list(term)
                if occurrence_list and doc_id in occurrence_list.documents:
                    positions = occurrence_list.documents[doc_id]
                    frequency = len(positions)
                    position_score = 1.0 / (1 + min(positions)) if positions else 0
                    score += frequency * (1 + position_score)
            
            scores[doc_id] = score
            
        # Sort by score
        ranked_results = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return ranked_results

    def get_snippet(self, doc_id, query_terms, max_length=200):
        """
        Generate a relevant text snippet from the document containing query terms
        """
        if doc_id not in self.documents:
            return ""

        content = self.documents[doc_id]['content']
        
        # Split content into words
        words = content.lower().split()
        
        # Find the best window containing most query terms
        best_start = 0
        best_count = 0
        window_size = 30  # Number of words in snippet
        
        for i in range(len(words) - window_size + 1):
            window = ' '.join(words[i:i + window_size])
            count = sum(1 for term in query_terms if term.lower() in window)
            
            if count > best_count:
                best_count = count
                best_start = i
        
        # Get the snippet
        snippet_words = words[best_start:best_start + window_size]
        snippet = ' '.join(snippet_words)
        
        # Truncate if too long
        if len(snippet) > max_length:
            snippet = snippet[:max_length] + '...'
        
        return snippet

    def get_document_title(self, doc_id):
        """
        Get the title of a document
        """
        if doc_id in self.documents:
            return self.documents[doc_id]['title']
        return ""

    def get_document_url(self, doc_id):
        """
        Get the URL of a document
        """
        if doc_id in self.documents:
            return self.documents[doc_id]['url']
        return ""