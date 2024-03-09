import os
import sys
import json
import concurrent.futures
from partial_index import PartialIndex
from inverted_index import InvertedIndex
from bs4 import BeautifulSoup
from functools import partial

total_documents = 0
partial_index_counter = 0
ngrams_list = []
indexed_hashes = set()

def get_memory_usage():
    # Function to monitor memory usage
    return sys.getsizeof({})

def extract_text(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Check if the soup object is not None and contains HTML tags
        if soup and soup.find():
            # Remove script and style tags
            for script in soup(["script", "style"]):
                script.extract()
            # Get text
            return soup.get_text(separator=' ')
        else:
            # If the soup object is None or does not contain HTML tags, return an empty string
            return ""
    except Exception as e:
        # If an exception occurs during parsing, print the error message and return an empty string
        print("Exception occurred during HTML parsing:", e)
        return ""

def index_file(file_path):
    # Function to extract text from file
    with open(file_path, 'r') as file:
        json_content = file.read()
        data = json.loads(json_content)
        url = data["url"]
        text = data["content"]
        text = extract_text(text)  # Extract text from HTML
    return text, url

# Function to calculate the hash of content
def calculate_hash(content):
    hash_object = hashlib.md5(content.encode())  # You can use other hash functions like sha256
    return hash_object.hexdigest()

# Using ngrams, calculate content similarity and returns true if it is over the threshold of 90%
def check_content_similarity(text):
    global ngrams_list
    this_ngram = compute_ngrams(text, n=3)
    for ngram in ngrams_list:
        similarity = compute_ngram_similarity(this_ngram, ngram)
        if similarity > 0.9:
            return True
    ngrams_list.append(this_ngram)
    return False

# Given a text, compute a list of ngrams of size n
def compute_ngrams(text, n):
    words = text.split()
    ngrams = []
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        ngrams.append(ngram)
    return ngrams

# Compute similarity given two lists of ngrams
def compute_ngram_similarity(ngram1, ngram2): # https://pythonhosted.org/ngram/tutorial.html
    intersection = len(set(ngram1) & set(ngram2))
    union = len(set(ngram1) | set(ngram2))
    similarity = intersection / union if union != 0 else 0
    return similarity

def index_files_in_directory(directory, memory_threshold):
    global total_documents
    global partial_index_counter
    current_memory_usage = get_memory_usage()
    
    # Create inverted indexes
    master_index = InvertedIndex()
    title_index = InvertedIndex()
    headings_index = InvertedIndex()

    partial_index = PartialIndex()
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".json"):
                file_path = os.path.join(root, file_name)
                text, url = index_file(file_path)
                
                # # Calculate hash of content
                # content_hash = calculate_hash(text)
                
                # # Check if content hash already exists
                # if content_hash in indexed_hashes:
                #     # Skip indexing if duplicate content
                #     continue
                
                # if check_content_similarity(text):
                #     continue
                
                # # Add hash to set of indexed hashes
                # indexed_hashes.add(content_hash)
                
                # Extract title and headings
                soup = BeautifulSoup(text, 'html.parser')
                title = soup.title.get_text() if soup.title else ""
                headings = " ".join([heading.get_text() for heading in soup.find_all(['h1', 'h2', 'h3'])])
                
                # Index the document
                partial_index.index_document(text, title, headings, url)
                
                total_documents += 1

                # Check memory usage and offload if necessary
                current_memory_usage += get_memory_usage()
                if current_memory_usage > memory_threshold:
                    master_index.merge_partial_index(partial_index)
                    partial_index.offload(f"partial_index_{partial_index_counter}.json")
                    partial_index.write_mapping_to_file("mapping.json")
                    partial_index = PartialIndex()  # Reset the partial index
                    partial_index_counter += 1
                    current_memory_usage = get_memory_usage()
                    

    # Offload any remaining documents
    if partial_index.index:
        partial_index.offload(f"partial_index_{partial_index_counter}.json")
        partial_index.write_mapping_to_file("mapping.json")
        master_index.merge_partial_index(partial_index)
  
        
    # Write indexes to separate files
    master_index.write_index_to_file("master_index.txt")
    
    # Report total docs 
    with open("total_documents.txt", "w") as f:
        f.write(str(total_documents))
        
    print("END")
    

def main():
    print("START")
    
    # Check if directory path is provided as command-line argument
    if len(sys.argv) < 2:
        print("Please include the path to the directory (eg /home/mannison/inf141/Assignment3/inf141assn3/corpus/developer/DEV/test)")
        return

    # Directory containing files to index
    directory = sys.argv[1]

    # Threshold for memory usage (in bytes)
    memory_threshold = 500000  # Adjust as needed

    # Initialize thread pool executor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a list of tasks to submit
        tasks = [executor.submit(index_files_in_directory, directory, memory_threshold)]
        
        # Wait for all tasks to complete
        concurrent.futures.wait(tasks)

if __name__ == '__main__':
    main()
