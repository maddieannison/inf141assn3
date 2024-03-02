import os
import sys
import json

from partial_index import PartialIndex
from inverted_index import InvertedIndex
from bs4 import BeautifulSoup

# Function to monitor memory usage
def get_memory_usage():
    return sys.getsizeof({})

def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style tags
    for script in soup(["script", "style"]):
        script.extract()
    # Get text
    return soup.get_text(separator=' ')

def main():
    # index = InvertedIndex()
    
    dir = "/home/mannison/inf141/Assignment3/inf141assn3/corpus/developer/DEV/test" #TODO take in as param
    # # index.index_files(dir)
    
    # Create an instance of InvertedIndex
    master_index = InvertedIndex()

    # Threshold for memory usage (in bytes)
    memory_threshold = 1024 * 1  # TODO calculate correct value
    print(f"MEMORY THRESHOLD {memory_threshold}")

    # Initialize memory usage
    current_memory_usage = get_memory_usage()

    # Create a PartialIndex
    partial_index = PartialIndex()
    partial_index_counter = 1

    
    # Index files in the directory
    for root, dirs, files in os.walk(dir):
        for file_name in files:
            if file_name.endswith(".json"):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r') as file:
                    json_content = file.read()
                    text = json.loads(json_content)["content"]
                    text = extract_text(text)  # Extract text from HTML
                    partial_index.index_document(file_name, text)

                # Check memory usage and offload if necessary
                current_memory_usage += get_memory_usage()
                # print(f" MEMORY:{current_memory_usage}")
                if current_memory_usage > memory_threshold:
                    partial_index.offload(f"partial_index_{partial_index_counter}.json")
                    master_index.merge_partial_index(PartialIndex.load(f"partial_index_{partial_index_counter}.json"))
                    partial_index_counter += 1
                    partial_index = PartialIndex()
                    current_memory_usage = get_memory_usage()

    # Merge the last partial index into the master index
    master_index.merge_partial_index(partial_index)
    
    # Clean up partial index files
    for i in range(1, partial_index_counter):
        filename = f"partial_index_{i}.json"
        if os.path.exists(filename):
            os.remove(filename)

    # Print the master index to a file
    master_index.write_index_to_file("report.txt")
   
if __name__ == '__main__':
    main()