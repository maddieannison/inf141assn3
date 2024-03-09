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

# Function to monitor memory usage
def get_memory_usage():
    return sys.getsizeof({})

def extract_text(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        print("Exception occurred:", e)
    # Remove script and style tags
    for script in soup(["script", "style"]):
        script.extract()
    # Get text
    return soup.get_text(separator=' ')

def index_file(file_path):
    with open(file_path, 'r') as file:
        json_content = file.read()
        text = json.loads(json_content)["content"]
        text = extract_text(text)  # Extract text from HTML
    return text

def index_files_in_directory(directory, memory_threshold):
    global total_documents
    global partial_index_counter
    current_memory_usage = get_memory_usage()
    
    master_index = InvertedIndex()

    partial_index = PartialIndex()
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".json"):
                file_path = os.path.join(root, file_name)
                text = index_file(file_path)
                partial_index.index_document(file_name, text)
                print(f"INDEX DOCUMENT {total_documents}")
                total_documents += 1

                # Check memory usage and offload if necessary
                current_memory_usage += get_memory_usage()
                if current_memory_usage > memory_threshold:
                    master_index.merge_partial_index(partial_index)
                    partial_index.offload(f"partial_index_{partial_index_counter}.json")
                    partial_index = PartialIndex()  # Reset the partial index
                    partial_index_counter += 1
                    current_memory_usage = get_memory_usage()
                    

    # Offload any remaining documents
    if partial_index.index:
        partial_index.offload(f"partial_index_{partial_index_counter}.json")
        master_index.merge_partial_index(partial_index)
        print("DONE")
        
    master_index.write_index_to_file("master_index.txt")
    with open("total_documents.txt", "w") as f:
        f.write(str(total_documents))
    

def main():
    # Directory containing files to index
    directory = "/home/mannison/inf141/Assignment3/inf141assn3/corpus/developer/DEV" # TODO take in as a param

    # Threshold for memory usage (in bytes)
    memory_threshold = 500000  # Adjust as needed

    # Initialize thread pool executor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a list of tasks to submit
        tasks = [executor.submit(index_files_in_directory, directory, memory_threshold)]
        
        # Wait for all tasks to complete
        concurrent.futures.wait(tasks)

    # # Remove partial index files
    # for i in range(0, partial_index_counter):
    #     filename = f"partial_index_{i}.json"
    #     if os.path.exists(filename):
    #         os.remove(filename)

if __name__ == '__main__':
    main()
