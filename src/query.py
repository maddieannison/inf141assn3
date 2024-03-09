import sys

from search_engine import SearchEngine

def main():
    # Read total document count from file
    with open("total_documents.txt", "r") as f:
        total_documents = int(f.read())
    
    search_engine = SearchEngine("master_index.txt", total_documents, "mapping.json")
    
    while True:
        query = input("Enter your query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        relevant_docs, elapsed_time = search_engine.search(query)
        print("Relevant documents:", relevant_docs[:10])
        print("Time taken:", elapsed_time, "seconds")


if __name__ == '__main__':
    main()
        
        
        