import re
import time
import math

from nltk.stem import PorterStemmer
from inverted_index import InvertedIndex

class SearchEngine:
    def __init__(self, master_index_file, total_documents):
        self.master_index = self.load_index(master_index_file)
        self.total_documents = total_documents
        self.stemmer = PorterStemmer()
        self.mapping_file = mapping_file
        self.doc_id_mapping = self.load_mapping(mapping_file)

    
    def load_mapping(self, mapping_file):
        with open(mapping_file, 'r') as f:
            return json.load(f)
        
    def load_index(self, filename):
        index = InvertedIndex()
        index.load_index_from_file(filename)
        return index
    
    def search(self, query):
        start_time = time.time()  # Record start time
        query_tokens = self.tokenize_and_stem(query)
        relevant_docs = None
        
        # Find documents containing each query term
        for token in query_tokens:
            stemmed_token = self.stemmer.stem(token)
            if stemmed_token in self.master_index.index:                
                if relevant_docs is None:
                    relevant_docs = set(self.master_index.index[token].keys())
                else:
                    relevant_docs.intersection_update(self.master_index.index[token].keys())
            else:
                # If any term is not found, no need to continue
                relevant_docs = set()
                break
            
        tfidf_scores = {}
        for doc_id in relevant_docs:
                tfidf_scores[doc_id] = self.calculate_tfidf(doc_id, query_tokens)
                
        # Sort documents based on TF-IDF scores
        sorted_doc_ids = sorted(tfidf_scores.keys(), key=lambda doc_id: tfidf_scores[doc_id], reverse=True)
        
        # Print filenames associated with relevant document IDs
        for doc_id in sorted_doc_ids:
            filename = self.get_filename_from_doc_id(doc_id)
            print(f"Document ID: {doc_id}, Filename: {filename}")

        # # Convert relevant_docs to a list and sort them by term frequency
        # sorted_doc_ids = sorted(relevant_docs, key=lambda doc_id: self.calculate_term_frequency(doc_id, query_tokens), reverse=True)
        
        end_time = time.time()  # Record end time
        elapsed_time = end_time - start_time  # Calculate elapsed time

        return sorted_doc_ids, elapsed_time

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
                # # Adjust IDF based on term location
                # if doc_id in self.title_index.index[token]:
                #     idf *= 2  # Double the IDF if term is in title
                # elif doc_id in self.headings_index.index[token]:
                #     idf *= 1.5  # Increase IDF by 50% if term is in headings
                # Calculate TF-IDF                
                tfidf_score += tf * idf
        return tfidf_score
    
    def tokenize_and_stem(self, text):
        # Tokenize and stem the query terms
        tokens = re.findall(r'\b\w+\b', text.lower())
        stemmed_tokens = [self.stemmer.stem(token) for token in tokens]
        return stemmed_tokens
    
    def get_filename_from_doc_id(self, doc_id):
        return self.doc_id_mapping.get(str(doc_id))

