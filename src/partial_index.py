import re
import json
import os
from collections import defaultdict

class PartialIndex:
    def __init__(self):
        # Initialize main index and document ID mapping
        self.index = defaultdict(dict)  # Main index with default dictionary
        self.doc_id_mapping = {}  # Mapping of document URLs to document IDs
        self.current_doc_id = 1  # Counter for assigning document IDs
    
    def tokenize(self, text):
        # Tokenizes the input text
        return re.findall(r'\b\w+\b', text.lower())

    def index_document(self, text, title, headings, url, title_weight=2, heading_weight=1.5):
        # Assign a unique document ID and map to URL
        doc_id = self.current_doc_id
        self.doc_id_mapping[url] = doc_id
        
        # Tokenize and index text, title, and headings
        for content, weight in [(text, 1), (title, title_weight), (headings, heading_weight)]:
            tokens = self.tokenize(content)
            for token in tokens:
                # Update index with token occurrences and respective weights
                self.index[token][doc_id] = self.index[token].get(doc_id, 0) + weight

        self.current_doc_id += 1

    def offload(self, filename):
        # Offloads the index to a JSON file
        with open(filename, 'w') as f:
            json.dump(self.index, f)

    def write_mapping_to_file(self, mapping_filename):
        # Writes the document ID mapping to a JSON file
        if os.path.exists(mapping_filename):
            with open(mapping_filename, 'r') as f:
                existing_mapping = json.load(f)
            self.doc_id_mapping.update(existing_mapping)

        with open(mapping_filename, 'w') as f:
            json.dump(self.doc_id_mapping, f)

    def load(filename):
        # Loads the index from a JSON file
        partial_index = PartialIndex()
        with open(filename, 'r') as file:
            partial_index.index = json.load(file)
        return partial_index
