# main.py

from src.trie import Trie
from src.text_processor import TextProcessor
from src.crawler import WebCrawler
from src.searcher import SearchEngine
from src.indexer import Indexer

def main():
    # Initialize components
    crawler = WebCrawler()
    processor = TextProcessor()
    trie = Trie()
    
    # Wikipedia pages to crawl
    start_urls = [
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "https://en.wikipedia.org/wiki/Data_structure",
        "https://en.wikipedia.org/wiki/Algorithm",
        "https://en.wikipedia.org/wiki/Computer_programming",
        "https://en.wikipedia.org/wiki/Software_engineering",
        "https://en.wikipedia.org/wiki/Database"
    ]

    print("Crawling Wikipedia pages...")
    documents = crawler.crawl_wikipedia_pages(start_urls)

    # Create and build index
    indexer = Indexer(trie)
    indexer.build_index(documents, processor)
    
    # Initialize search engine
    search_engine = SearchEngine(trie, documents)

    # Search interface
    while True:
        print("\n" + "="*50)
        query = input("Enter search query (or 'quit' to exit): ").strip()
        
        if query.lower() == 'quit':
            break
        
        if not query:
            print("Please enter a valid query.")
            continue

        # Process query
        processed_query = processor.process_query(query)
        
        if not processed_query:
            print("No valid search terms after processing.")
            continue

        # Perform search
        results = search_engine.search(query)
        
        if not results:
            print(f"\nNo results found for '{query}'")
            continue

        print(f"\nFound {len(results)} results for '{query}':")
        
        for doc_id, score in results:
            print("\n" + "-"*50)
            print(f"Document: {search_engine.get_document_title(doc_id)}")
            print(f"Score: {score:.4f}")
            print(f"URL: {search_engine.get_document_url(doc_id)}")
            
            # Generate and display snippet
            snippet = search_engine.get_snippet(doc_id, processed_query)
            print(f"Snippet: {snippet}")


if __name__ == "__main__":
    main()