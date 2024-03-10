import json
import re
import os

from bs4 import BeautifulSoup
from collections import defaultdict

class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(dict)
        self.partial_indexes = []
                        
    def merge_partial_index(self, partial_index):
        # Merge the partial index with the current master index
        for token, postings in partial_index.index.items():
            for doc_id, freq in postings.items():
                if doc_id in self.index[token]:
                    self.index[token][doc_id] += freq
                else:
                    self.index[token][doc_id] = freq
            
    def write_index_to_file(self, filename):
        # Write the index to a file and format
        with open(filename, 'w') as f:
            for token, postings in self.index.items():
                f.write(f"Token: {token}\n")
                for document_id, frequency in postings.items():
                    f.write(f"  Document ID: {document_id}, Frequency: {frequency} \n")
                f.write("\n")
    
    def load_index_from_file(self, filename):
        with open(filename, 'r') as f:
            current_token = None
            postings = {}

            for line in f:
                line = line.strip()

                if line.startswith("Token:"):
                    if current_token:
                        self.index[current_token] = postings
                        postings = {}
                    current_token = line.split(":")[1].strip()

                elif line.startswith("Document ID:"):
                    doc_info = line.split(",")
                    doc_id = int(doc_info[0].split(":")[1].strip())
                    frequency = round(float(doc_info[1].split(":")[1].strip()), 2)
                    postings[doc_id] = frequency

            if current_token:
                self.index[current_token] = postings

        print("Index loaded successfully.")
