import re
import json

from collections import defaultdict

class PartialIndex:
    def __init__(self):
        self.index = defaultdict(dict)
        self.doc_id_mapping = {}
        self.current_doc_id = 1
        
    def index_document(self, filename, text):
        doc_id = self.current_doc_id
        self.doc_id_mapping[filename] = doc_id
        # Tokenize content        
        tokens = re.findall(r'\b\w+\b', text.lower())
        for token in tokens:
            if token in self.index:
                if doc_id in self.index[token]:
                    self.index[token][doc_id] += 1
                else:
                    self.index[token][doc_id] = 1
            else:
                self.index[token] = {doc_id: 1}
        self.current_doc_id += 1
                
    def offload(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.index, f)
    
    def load(filename):
        partial_index = PartialIndex()
        with open(filename, 'r') as file:
            partial_index.index = json.load(file)
        return partial_index