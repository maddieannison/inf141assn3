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
        self.mapping = self.load_mapping()
        
    def load_mapping(self):
        # Load the JSON file
        with open(self.mapping_file, 'r') as file:
            mapping = json.load(file)
        return mapping

        
    def load_index(self, filename):
        # Function to load the index in from memory
        index = InvertedIndex()
        print("LOADING")
        index.load_index_from_file(filename)
        print("LOADED")
        return index
    
    def search(self, query):
        # Search function
        start_time = time.time()  # Record start time
        query_tokens = self.tokenize_and_stem(query)
        relevant_docs = self.find_relevant_documents(query_tokens)
            
        # Extract document IDs from the set of relevant documents
        doc_ids = list(relevant_docs)
        
        # Calculate TF-IDF scores for the relevant documents
        tfidf_scores = [(doc_id, self.calculate_tfidf(doc_id, query_tokens)) for doc_id in doc_ids]
        
        # Sort documents by TF-IDF scores in descending order
        sorted_docs = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
        
        # Extract URLs from the sorted list of documents (top ten)
        urls = [self.get_url_from_doc_id(doc_id) for doc_id, _ in sorted_docs[:10]]
                
        end_time = time.time()  # Record end time
        elapsed_time = end_time - start_time  # Calculate elapsed time

        return urls, elapsed_time
    
    def find_relevant_documents(self, query_tokens):
        # Find relevant documents based on query terms using the inverted index
        relevant_docs = None
        for token in query_tokens:
            if token in self.master_index.index:
                if relevant_docs is None:
                    relevant_docs = set(self.master_index.index[token].keys())
                else:
                    relevant_docs.intersection_update(self.master_index.index[token].keys())
        if relevant_docs is None:
            return set()
        else:
            return relevant_docs

    def calculate_term_frequency(self, doc_id, query_tokens):
        # Function to calculate the term frequency
        term_frequency = 0
        for token in query_tokens:
            if token in self.master_index.index and doc_id in self.master_index.index[token]:
                term_frequency += self.master_index.index[token][doc_id]
        return term_frequency
    
    def calculate_tfidf(self, doc_id, query_tokens):
        # Function to calculate the tf-idf
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
        # Check if the document ID exists in the mapping
        for url, mapped_id in self.mapping.items():
            if mapped_id == doc_id:
                return url
        
        return "URL not found for the given document ID"

