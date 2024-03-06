import re
import time

from inverted_index import InvertedIndex

class SearchEngine:
    def __init__(self, master_index_file):
        self.master_index = self.load_master_index(master_index_file)

    def load_master_index(self, filename):
        master_index = InvertedIndex()
        master_index.load_index_from_file(filename)
        return master_index
    
    def search(self, query):
        start_time = time.time()  # Record start time
        query_tokens = re.findall(r'\b\w+\b', query.lower())
        relevant_docs = None
        
        # Find documents containing each query term
        for token in query_tokens:
            if token in self.master_index.index:
                if relevant_docs is None:
                    relevant_docs = set(self.master_index.index[token].keys())
                else:
                    relevant_docs.intersection_update(self.master_index.index[token].keys())
            else:
                # If any term is not found, no need to continue
                relevant_docs = set()
                break

        # Convert relevant_docs to a list and sort them by term frequency
        sorted_doc_ids = sorted(relevant_docs, key=lambda doc_id: self.calculate_term_frequency(doc_id, query_tokens), reverse=True)
        
        end_time = time.time()  # Record end time
        elapsed_time = end_time - start_time  # Calculate elapsed time

        return sorted_doc_ids, elapsed_time

    def calculate_term_frequency(self, doc_id, query_tokens):
        term_frequency = 0
        for token in query_tokens:
            if token in self.master_index.index and doc_id in self.master_index.index[token]:
                term_frequency += self.master_index.index[token][doc_id]
        return term_frequency

