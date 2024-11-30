# src/indexer.py

from collections import defaultdict
import math
import json
import os

class Indexer:
    def __init__(self, trie):
        self.trie = trie
        self.document_vectors = {}  # For storing document vectors
        self.total_documents = 0
        self.index_stats = {
            'total_documents': 0,
            'total_terms': 0,
            'average_document_length': 0
        }
    
    def build_index(self, documents, processor):
        """
        Build the index from documents
        """
        print("Building index...")
        self.total_documents = len(documents)
        total_terms = 0
        total_length = 0
        
        for doc_id, doc_data in documents.items():
            print(f"Indexing document {doc_id}: {doc_data['title']}")
            
            # Process document text
            word_positions = processor.process_document(doc_data['content'], doc_id)
            
            # Update document length
            doc_length = sum(len(positions) for positions in word_positions.values())
            total_length += doc_length
            
            # Create document vector
            self.document_vectors[doc_id] = defaultdict(int)
            
            # Add terms to trie and update document vector
            for word, positions in word_positions.items():
                total_terms += len(positions)
                self.document_vectors[doc_id][word] = len(positions)
                
                for position in positions:
                    self.trie.insert(word, doc_id, position)
        
        # Update index statistics
        self.index_stats.update({
            'total_documents': self.total_documents,
            'total_terms': total_terms,
            'average_document_length': total_length / self.total_documents if self.total_documents > 0 else 0
        })
        
        print("Indexing completed!")
        self._print_index_stats()
    
    def calculate_bm25_score(self, query_terms, doc_id, k1=1.5, b=0.75):
        """
        Calculate BM25 score for a document
        """
        score = 0
        doc_length = sum(self.document_vectors[doc_id].values())
        avg_doc_length = self.index_stats['average_document_length']
        
        for term in query_terms:
            # Get term frequency in document
            is_found, node = self.trie.search(term)
            if not is_found:
                continue
                
            tf = node.document_references.get(doc_id, 0)
            
            # Calculate IDF
            docs_with_term = len(node.document_references)
            idf = math.log((self.total_documents - docs_with_term + 0.5) / 
                          (docs_with_term + 0.5) + 1)
            
            # Calculate BM25 score for term
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * doc_length / avg_doc_length)
            score += idf * numerator / denominator
        
        return score
    
    def save_index(self, filepath):
        """
        Save index statistics and document vectors to file
        """
        index_data = {
            'stats': self.index_stats,
            'vectors': self.document_vectors
        }
        
        with open(filepath, 'w') as f:
            json.dump(index_data, f)
    
    def load_index(self, filepath):
        """
        Load index statistics and document vectors from file
        """
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                index_data = json.load(f)
                self.index_stats = index_data['stats']
                self.document_vectors = index_data['vectors']
    
    def _print_index_stats(self):
        """
        Print index statistics
        """
        print("\nIndex Statistics:")
        print(f"Total Documents: {self.index_stats['total_documents']}")
        print(f"Total Terms: {self.index_stats['total_terms']}")
        print(f"Average Document Length: {self.index_stats['average_document_length']:.2f}")