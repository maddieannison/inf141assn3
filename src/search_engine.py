import re
import time
import math
import json

from nltk.stem import PorterStemmer
from inverted_index import InvertedIndex

class SearchEngine:
    def __init__(self, master_index_file, total_documents, mapping_file):
        self.master_index = self.load_index(master_index_file)
        self.total_documents = total_documents
        self.stemmer = PorterStemmer()
        self.mapping_file = mapping_file
        self.doc_id_mapping = self.load(mapping_file)

    
    def load(self, file):
        try:
            with open(file, 'r') as f:
                self.doc_id_mapping = json.load(f)
        except FileNotFoundError:
            print(f"Mapping file '{file}' not found.")
            self.doc_id_mapping = {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from mapping file '{file}'.")
            self.doc_id_mapping = {}
        
    def load_index(self, filename):
        index = InvertedIndex()
        index.load_index_from_file(filename)
        return index
    
    def search(self, query):
        start_time = time.time()  # Record start time
        query_tokens = self.tokenize_and_stem(query)
        relevant_docs = []  # Initialize list for relevant documents with URLs
        
        # Find documents containing each query term
        for token in query_tokens:
            if token in self.master_index.index:                
                relevant_docs.extend(self.master_index.index[token].keys())      

        tfidf_scores = {}
        for doc_id in relevant_docs:
            tfidf_scores[doc_id] = self.calculate_tfidf(doc_id, query_tokens)
                
        # Sort documents based on TF-IDF scores
        sorted_doc_ids = sorted(tfidf_scores.keys(), key=lambda doc_id: tfidf_scores[doc_id], reverse=True)
        
        # Populate relevant_docs list with (doc_id, url) tuples
        relevant_docs = [(doc_id, self.get_url_from_doc_id(doc_id)) for doc_id in sorted_doc_ids]
        
        # Extract URLs from the list of tuples
        urls = [url for doc_id, url in relevant_docs if isinstance(url, str)]
            
        end_time = time.time()  # Record end time
        elapsed_time = end_time - start_time  # Calculate elapsed time

        return urls, elapsed_time

    def calculate_term_frequency(self, doc_id, query_tokens):
        term_frequency = 0
        for token in query_tokens:
            if token in self.master_index.index and doc_id in self.master_index.index[token]:
                term_frequency += self.master_index.index[token][doc_id]
        return term_frequency
    
    def calculate_tfidf(self, doc_id, query_tokens):
        tfidf_score = 0
        for token in query_tokens:
            if token in self.master_index.index and doc_id in self.master_index.index[token]:
                # Calculate TF
                tf = self.master_index.index[token][doc_id]
                # Calculate IDF
                idf = math.log(self.total_documents / len(self.master_index.index[token]))             
                tfidf_score += tf * idf
        return tfidf_score
    
    def tokenize_and_stem(self, text):
        # Tokenize and stem the query terms
        tokens = re.findall(r'\b\w+\b', text.lower())
        stemmed_tokens = [self.stemmer.stem(token) for token in tokens]
        return stemmed_tokens
    
    def get_url_from_doc_id(self, doc_id):
        # Load the JSON file
        with open('mapping.json', 'r') as file:
            mapping = json.load(file)
        
        # Check if the document ID exists in the mapping
        for url, mapped_id in mapping.items():
            if mapped_id == doc_id:
                return url
        
        return "URL not found for the given document ID"

