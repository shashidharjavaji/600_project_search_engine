# src/crawler.py

import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin, urlparse

class WebCrawler:
    def __init__(self):
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def extract_links(self, soup, base_url):
        """
        Extract all links from the page
        """
        links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/wiki/'):
                full_url = urljoin('https://en.wikipedia.org', href)
                links.add(full_url)
        return links

    def get_wikipedia_content(self, url):
        """
        Fetch and extract main content from a Wikipedia page
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get title
            title = soup.find(id="firstHeading").text
            
            # Get main content
            content_div = soup.find(id="mw-content-text")
            if content_div:
                # Extract links before removing elements
                links = self.extract_links(content_div, url)
                
                # Remove unwanted elements
                for unwanted in content_div.find_all(['script', 'style', 'table', 'sup']):
                    unwanted.decompose()
                
                # Extract text from paragraphs
                paragraphs = content_div.find_all('p')
                content = ' '.join(p.get_text() for p in paragraphs)
                
                # Clean content
                content = re.sub(r'\[\d+\]', '', content)
                content = re.sub(r'\s+', ' ', content)
                
                return {
                    'title': title,
                    'content': content.strip(),
                    'url': url,
                    'links': links
                }
            
            return None
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
        
    def crawl_wikipedia_pages(self, start_urls, max_pages=10):  # Changed from 6 to 10
        """
        Crawl Wikipedia pages starting from given URLs
        """
        documents = {}
        doc_id = 1
        all_links = set()

        for url in start_urls:
            if doc_id > max_pages:
                break
                
            if url not in self.visited_urls:
                print(f"Crawling page {doc_id}/10: {url}")  # Updated progress message
                self.visited_urls.add(url)
                
                page_data = self.get_wikipedia_content(url)
                if page_data:
                    # Store the page data
                    documents[doc_id] = page_data
                    
                    # Add links to content for verification
                    links_text = "\n Related links: " + "\n".join(page_data['links'])
                    documents[doc_id]['content'] += links_text
                    
                    # Update all_links set
                    all_links.update(page_data['links'])
                    
                    doc_id += 1
                    
                # Be nice to Wikipedia's servers
                time.sleep(1)

        # Verify interconnected links
        for doc in documents.values():
            doc['has_internal_links'] = any(link in all_links for link in doc['links'])

        return documents
