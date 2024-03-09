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
        
    def load_index(self, filename):
        # Function to load the index in from memory
        index = InvertedIndex()
        index.load_index_from_file(filename)
        return index
    
    def search(self, query):
        # Search function
        start_time = time.time()  # Record start time
        query_tokens = self.tokenize_and_stem(query)
        relevant_docs = []  # Initialize list for relevant documents with URLs
            
        # Find documents containing each query term
        for doc_id in range(1, self.total_documents + 1):
            contains_all_terms = True
            for token in query_tokens:
                if token not in self.master_index.index or doc_id not in self.master_index.index[token]:
                    contains_all_terms = False
                    break
            if contains_all_terms:
                relevant_docs.append((doc_id, self.get_url_from_doc_id(doc_id)))
        
        # Extract URLs from the list of tuples
        urls = [url for doc_id, url in relevant_docs if isinstance(url, str)]
                
        end_time = time.time()  # Record end time
        elapsed_time = end_time - start_time  # Calculate elapsed time

        return urls, elapsed_time

        # # Search function
        # start_time = time.time()  # Record start time
        # query_tokens = self.tokenize_and_stem(query)
        # relevant_docs_sets = []  # Initialize list for sets of relevant documents
            
        # # Find documents containing each query term
        # for token in query_tokens:
        #     if token in self.master_index.index:                
        #         relevant_docs_sets.append(set(self.master_index.index[token].keys()))
        
        # # Calculate the intersection of relevant document sets
        # if relevant_docs_sets:
        #     intersection = set.intersection(*relevant_docs_sets)
        # else:
        #     intersection = set()
        
        # # Filter documents to include only those containing all query terms
        # relevant_docs = []
        # for doc_id in intersection:
        #     if all(doc_id in docs_set for docs_set in relevant_docs_sets):
        #         relevant_docs.append((doc_id, self.get_url_from_doc_id(doc_id)))
        
        # # Extract URLs from the list of tuples
        # urls = [url for doc_id, url in relevant_docs if isinstance(url, str)]
                
        # end_time = time.time()  # Record end time
        # elapsed_time = end_time - start_time  # Calculate elapsed time

        # return urls, elapsed_time

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
        # Load the JSON file
        with open(self.mapping_file, 'r') as file:
            mapping = json.load(file)
        
        # Check if the document ID exists in the mapping
        for url, mapped_id in mapping.items():
            if mapped_id == doc_id:
                return url
        
        return "URL not found for the given document ID"

