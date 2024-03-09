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
                
    def load_index_from_file(self, filename):
        with open(filename, 'r') as f:
            # Read the content of the file
            lines = f.readlines()

            # Initialize variables to store token and postings
            current_token = None
            postings = {}

            # Parse each line in the file
            for line in lines:
                line = line.strip()

                # If the line starts with "Token:", it indicates a new token
                if line.startswith("Token:"):
                    # Extract the token
                    current_token = line.split(":")[1].strip()
                    postings = {}

                # If the line starts with "Document ID:", it indicates a posting
                elif line.startswith("Document ID:"):
                    # Extract document ID and frequency
                    doc_info = line.split(",")
                    doc_id = int(doc_info[0].split(":")[1].strip())
                    frequency = int(round(float(doc_info[1].split(":")[1].strip())))

                    # Add the posting to the postings dictionary
                    postings[doc_id] = frequency

                # If the line is empty, it indicates the end of postings for the current token
                elif not line:
                    # Add the token and its postings to the index
                    if current_token:
                        self.index[current_token] = postings

        # Print loaded index
        print("Index loaded successfully.")
                
        