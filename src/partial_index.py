import re
import json

from collections import defaultdict

class PartialIndex:
    def __init__(self):
        self.index = defaultdict(dict)
        self.doc_id_mapping = {}
        self.current_doc_id = 1
        
    def index_document(self, filename, text, title, headings):
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
                
         # Index title and headings
        title_tokens = re.findall(r'\b\w+\b', title.lower())
        for token in title_tokens:
            if token in self.index:
                if doc_id in self.index[token]:
                    self.index[token][doc_id] += 2  # Double the weight for titles
                else:
                    self.index[token][doc_id] = 2
            else:
                self.index[token] = {doc_id: 2}  # Double the weight for titles
        
        headings_tokens = re.findall(r'\b\w+\b', headings.lower())
        for token in headings_tokens:
            if token in self.index:
                if doc_id in self.index[token]:
                    self.index[token][doc_id] += 1.5  # Increase the weight for headings
                else:
                    self.index[token][doc_id] = 1.5
            else:
                self.index[token] = {doc_id: 1.5}  # Increase the weight for headings
        
        self.current_doc_id += 1
                
    def offload(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.index, f)
            
    def write_mapping_to_file(self, mapping_filename):
        if os.path.exists(mapping_filename):
            # Load existing mapping from file
            with open(mapping_filename, 'r') as f:
                existing_mapping = json.load(f)
            
            # Merge existing mapping with current mapping
            self.doc_id_mapping.update(existing_mapping)
        
        # Write updated mapping to file
        with open(mapping_filename, 'w') as f:
            json.dump(self.doc_id_mapping, f)
            
    
    def load(filename):
        partial_index = PartialIndex()
        with open(filename, 'r') as file:
            partial_index.index = json.load(file)
        return partial_index