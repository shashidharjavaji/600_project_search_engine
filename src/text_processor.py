# src/text_processor.py

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import string

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

class TextProcessor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text):
        """
        Preprocess text by basic cleaning and converting to lowercase
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters while preserving important punctuation
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text):
        """
        Tokenize text into words
        """
        return word_tokenize(text)
    
    def remove_stop_words(self, tokens):
        """
        Remove stop words from token list
        """
        return [token for token in tokens if token not in self.stop_words]
    
    def stem_words(self, tokens):
        """
        Apply stemming to tokens
        """
        return [self.stemmer.stem(token) for token in tokens]
    
    def process_document(self, text, doc_id):
        """
        Process document and return words with their positions
        Returns: Dictionary of {word: [positions]}
        """
        # Preprocess text
        cleaned_text = self.preprocess_text(text)
        
        # Tokenize
        tokens = self.tokenize(cleaned_text)
        
        # Remove stop words
        tokens = self.remove_stop_words(tokens)
        
        # Create word positions dictionary
        word_positions = {}
        
        for position, token in enumerate(tokens):
            # Stem the token
            stemmed_token = self.stemmer.stem(token)
            
            if stemmed_token not in word_positions:
                word_positions[stemmed_token] = []
            word_positions[stemmed_token].append(position)
        
        return word_positions
    
    def process_query(self, query):
        """
        Process search query
        Returns: List of processed query terms
        """
        # Preprocess query
        cleaned_query = self.preprocess_text(query)
        
        # Tokenize
        tokens = self.tokenize(cleaned_query)
        
        # Remove stop words
        tokens = self.remove_stop_words(tokens)
        
        # Stem tokens
        tokens = self.stem_words(tokens)
        
        return tokens

    def get_original_words(self, text):
        """
        Get original words (before stemming) for context
        """
        cleaned_text = self.preprocess_text(text)
        tokens = self.tokenize(cleaned_text)
        return [token for token in tokens if token not in self.stop_words]