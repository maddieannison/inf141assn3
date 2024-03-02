import json
import re
import os

from bs4 import BeautifulSoup
from collections import defaultdict

class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(dict)
                        
    def merge_partial_index(self, partial_index):
        for token, postings in partial_index.index.items():
            for doc_id, freq in postings.items():
                if doc_id in self.index[token]:
                    self.index[token][doc_id] += freq
                else:
                    self.index[token][doc_id] = freq
                
                
    def write_index_to_file(self, filename):
        with open(filename, 'w') as f:
            for token, postings in self.index.items():
                f.write(f"Token: {token}\n")
                for document_id, frequency in postings.items():
                    f.write(f"  Document ID: {document_id}, Frequency: {frequency} \n")
                f.write("\n")
                
        