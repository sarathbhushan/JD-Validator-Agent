import pandas as pd
import chromadb
import uuid
from chardet import detect

class Portfolio:
    def __init__(self):
        file_path = "resource/my_portfolio.csv"
        
        # Detect file encoding
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            detected = detect(raw_data)
            encoding = detected['encoding']
        
        # Try detected encoding first, then fallback to common encodings
        encodings_to_try = [encoding, 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for enc in encodings_to_try:
            try:
                self.data = pd.read_csv(file_path, encoding=enc)
                break  # If successful, exit the loop
            except (UnicodeDecodeError, LookupError):
                continue
        else:
            raise ValueError(f"Failed to read CSV with any of these encodings: {encodings_to_try}")

        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def clear_collection(self):
        """Clear all documents from the collection"""
        # Get all document IDs
        if self.collection.count() > 0:
            # Get all documents to retrieve their IDs
            results = self.collection.get()
            if results and results['ids']:
                # Delete all documents using their IDs
                self.collection.delete(ids=results['ids'])
        # Recreate the collection
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self, force_reload=False):
        """Load portfolio data into the vector database"""
        if force_reload:
            self.clear_collection()
        
        # Only load if collection is empty
        if self.collection.count() == 0 and hasattr(self, 'data'):
            for _, row in self.data.iterrows():
                doc_id = str(uuid.uuid4())
                self.collection.add(
                    documents=[row["Techstack"]],
                    metadatas=[{"links": row["Links"]}],
                    ids=[doc_id]
                )

    def query_links(self, skills):
        return self.collection.query(query_texts=skills, n_results=2).get('metadatas', [])
