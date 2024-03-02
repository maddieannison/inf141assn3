import re
import json

from collections import defaultdict

class PartialIndex:
    def __init__(self):
        self.index = defaultdict(dict)
        
    def index_document(self, document_id, text):
        # Tokenize content        
        tokens = re.findall(r'\b\w+\b', text.lower())
        for token in tokens:
            if token in self.index:
                if document_id in self.index[token]:
                    self.index[token][document_id] += 1
                else:
                    self.index[token][document_id] = 1
            else:
                self.index[token] = {document_id: 1}
                
    def offload(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.index, f)
    
    def load(filename):
        partial_index = PartialIndex()
        with open(filename, 'r') as file:
            partial_index.index = json.load(file)
        return partial_index