import sys

from search_engine import SearchEngine

def main():
    search_engine = SearchEngine("master_index.txt")
    
    while True:
        query = input("Enter your query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        relevant_docs, elapsed_time = search_engine.search(query)
        print("Relevant documents:", relevant_docs)
        print("Time taken:", elapsed_time, "seconds")


if __name__ == '__main__':
    main()
        
        
        