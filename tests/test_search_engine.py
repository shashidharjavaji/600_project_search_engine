# tests/test_search_engine.py

import sys
import os
import unittest
from bs4 import BeautifulSoup
import requests
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trie import Trie, OccurrenceList
from src.text_processor import TextProcessor
from src.crawler import WebCrawler
from src.searcher import SearchEngine

class TestSearchEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test documents and initialize components"""
        print("\nInitializing Search Engine Components...")
        cls.trie = Trie()
        cls.processor = TextProcessor()
        cls.crawler = WebCrawler()
        
        # Test URLs (Wikipedia pages with hyperlinks between them)
        cls.test_urls = [
            "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "https://en.wikipedia.org/wiki/Data_structure",
            "https://en.wikipedia.org/wiki/Algorithm",
            "https://en.wikipedia.org/wiki/Computer_programming",
            "https://en.wikipedia.org/wiki/Software_engineering",
            "https://en.wikipedia.org/wiki/Database",
            "https://en.wikipedia.org/wiki/Machine_learning",
            "https://en.wikipedia.org/wiki/Artificial_intelligence",
            "https://en.wikipedia.org/wiki/Web_development",
            "https://en.wikipedia.org/wiki/Computer_science"
        ]
        
        # Crawl pages
        print("\nCrawling test pages...")
        cls.documents = cls.crawler.crawl_wikipedia_pages(cls.test_urls)
        
        # Build index
        print("\nBuilding index...")
        for doc_id, doc_data in cls.documents.items():
            print(f"Processing document {doc_id}: {doc_data['title']}")
            word_positions = cls.processor.process_document(doc_data['content'], doc_id)
            for word, positions in word_positions.items():
                for position in positions:
                    cls.trie.insert(word, doc_id, position)
        
        cls.search_engine = SearchEngine(cls.trie, cls.documents)
        print("\nSetup completed successfully!")

    def test_01_crawler_functionality(self):
        """Test web crawler functionality"""
        print("\nTesting crawler functionality...")
        self.assertGreater(len(self.documents), 0, "No documents were crawled")
        for doc_id, doc_data in self.documents.items():
            self.assertIn('title', doc_data, f"Document {doc_id} has no title")
            self.assertIn('content', doc_data, f"Document {doc_id} has no content")
            self.assertIn('url', doc_data, f"Document {doc_id} has no URL")
        print("Crawler functionality: PASSED")

    def test_02_trie_basic_operations(self):
        """Test basic trie operations"""
        print("\nTesting basic trie operations...")
        # Test insertion
        test_word = "testword"
        test_doc_id = 999
        test_position = 0
        
        self.trie.insert(test_word, test_doc_id, test_position)
        is_found, _ = self.trie.search(test_word)
        
        self.assertTrue(is_found, "Word not found after insertion")
        
        # Test non-existent word
        is_found, _ = self.trie.search("nonexistentword")
        self.assertFalse(is_found, "Found non-existent word")
        print("Basic trie operations: PASSED")

    def test_03_text_processor(self):
        """Test text processor functionality"""
        print("\nTesting text processor...")
        # Test stop words removal
        test_text = "the and of in to for"
        processed = self.processor.process_query(test_text)
        self.assertEqual(len(processed), 0, "Stop words not removed properly")
        
        # Test basic processing
        test_text = "Python Programming Language"
        processed = self.processor.process_query(test_text)
        self.assertGreater(len(processed), 0, "Text processing failed")
        print("Text processor functionality: PASSED")

    def test_04_search_functionality(self):
        """Test search functionality"""
        print("\nTesting search functionality...")
        # Test single word search
        results = self.search_engine.search("python")
        self.assertGreater(len(results), 0, "No results for 'python' search")
        
        # Test multiple word search
        results = self.search_engine.search("python programming")
        self.assertGreater(len(results), 0, "No results for multiple word search")
        
        # Test ranking order
        if len(results) >= 2:
            self.assertGreaterEqual(
                results[0][1], 
                results[1][1], 
                "Results not properly ranked"
            )
        print("Search functionality: PASSED")

    def test_05_boundary_conditions(self):
        """Test boundary conditions"""
        print("\nTesting boundary conditions...")
        
        # Test empty query
        results = self.search_engine.search("")
        self.assertEqual(len(results), 0, "Empty query returned results")
        
        # Test very long query
        long_query = "python " * 100
        results = self.search_engine.search(long_query)
        self.assertIsInstance(results, list, "Long query handling failed")
        
        # Test special characters
        special_chars = "!@#$%^&*()"
        results = self.search_engine.search(special_chars)
        self.assertEqual(len(results), 0, "Special characters not handled properly")
        
        # Test numeric input
        results = self.search_engine.search("123456")
        self.assertEqual(len(results), 0, "Numeric input not handled properly")
        print("Boundary conditions: PASSED")

    def test_06_case_sensitivity(self):
        """Test case sensitivity handling"""
        print("\nTesting case sensitivity...")
        lower_results = self.search_engine.search("python")
        upper_results = self.search_engine.search("PYTHON")
        self.assertEqual(
            len(lower_results), 
            len(upper_results), 
            "Case sensitivity not handled properly"
        )
        print("Case sensitivity handling: PASSED")

    def test_07_snippet_generation(self):
        """Test snippet generation"""
        print("\nTesting snippet generation...")
        results = self.search_engine.search("python")
        if results:
            doc_id = results[0][0]
            snippet = self.search_engine.get_snippet(doc_id, ["python"])
            self.assertIsInstance(snippet, str, "Snippet not generated properly")
            self.assertGreater(len(snippet), 0, "Empty snippet generated")
        print("Snippet generation: PASSED")

    def test_08_hyperlink_verification(self):
        """Test hyperlink verification"""
        print("\nTesting hyperlink verification...")
        link_count = 0
        for doc_data in self.documents.values():
            content = doc_data['content'].lower()
            for url in self.test_urls:
                if url.lower() in content:
                    link_count += 1
        
        print(f"Found {link_count} hyperlinks between documents")
        self.assertGreater(link_count, 0, "No hyperlinks found between documents")
        print("Hyperlink verification: PASSED")

    def test_09_document_processing(self):
        """Test document processing"""
        print("\nTesting document processing...")
        for doc_id, doc_data in self.documents.items():
            # Test document structure
            self.assertIn('title', doc_data)
            self.assertIn('content', doc_data)
            self.assertIn('url', doc_data)
            
            # Test content processing
            word_positions = self.processor.process_document(doc_data['content'], doc_id)
            self.assertIsInstance(word_positions, dict)
            self.assertGreater(len(word_positions), 0)
        print("Document processing: PASSED")

    def test_10_ranking_algorithm(self):
        """Test ranking algorithm"""
        print("\nTesting ranking algorithm...")
        query = "python programming"
        results = self.search_engine.search(query)
        
        if len(results) >= 2:
            # Verify results are sorted by score
            scores = [score for _, score in results]
            self.assertEqual(
                scores, 
                sorted(scores, reverse=True), 
                "Results not properly ranked"
            )
            
            # Verify score calculation
            doc_id, score = results[0]
            self.assertGreater(score, 0, "Invalid score calculation")
        print("Ranking algorithm: PASSED")

def run_tests():
    """Run all tests"""
    print("Starting Comprehensive Search Engine Tests...\n")
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == "__main__":
    run_tests()