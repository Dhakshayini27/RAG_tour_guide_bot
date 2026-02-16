"""
Create embeddings and store in vector database (ChromaDB).
"""
import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class VectorStore:
    """Handles embedding creation and vector storage."""
    
    def __init__(self, collection_name: str = "tour_guide", 
                 persist_directory: str = "chroma_db"):
        """
        Initialize vector store.
        
        Args:
            collection_name: Name for the ChromaDB collection
            persist_directory: Directory to persist the database
        """
        print("Initializing vector store...")
        
        # Initialize embedding model (runs locally, no API needed)
        print("Loading embedding model (this may take a moment)...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Embedding model loaded")
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Tour guide knowledge base"}
        )
        
        print(f"✓ Vector store ready (collection: {collection_name})")
    
    def add_documents(self, chunks: List[Dict[str, str]]):
        """
        Add document chunks to vector store.
        
        Args:
            chunks: List of chunks with 'content', 'source', 'chunk_id'
        """
        print(f"\nAdding {len(chunks)} chunks to vector store...")
        
        # Prepare data
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [
            {
                'source': chunk['source'],
                'chunk_id': str(chunk['chunk_id'])
            }
            for chunk in chunks
        ]
        ids = [f"{chunk['source']}_{chunk['chunk_id']}" for chunk in chunks]
        
        # Create embeddings
        print("Creating embeddings...")
        embeddings = self.embedding_model.encode(
            documents, 
            show_progress_bar=True,
            convert_to_numpy=True
        ).tolist()
        
        # Add to ChromaDB
        print("Storing in database...")
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✓ Successfully added {len(chunks)} chunks to vector store")
        print(f"  Total items in collection: {self.collection.count()}")
    
    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Search for relevant chunks.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        # Create query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'source': results['metadatas'][0][i]['source'],
                'chunk_id': results['metadatas'][0][i]['chunk_id'],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results
    
    def clear(self):
        """Clear all data from the collection."""
        # Delete and recreate collection
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"description": "Tour guide knowledge base"}
        )
        print("✓ Vector store cleared")


def build_vector_store(chunks: List[Dict[str, str]], 
                       collection_name: str = "tour_guide") -> VectorStore:
    """
    Build vector store from document chunks.
    
    Args:
        chunks: Document chunks to add
        collection_name: Name for the collection
        
    Returns:
        VectorStore instance
    """
    store = VectorStore(collection_name=collection_name)
    store.add_documents(chunks)
    return store


if __name__ == "__main__":
    # Test the vector store
    from load_docs import load_documents
    from chunk_docs import chunk_documents
    
    # Load and chunk documents
    docs = load_documents()
    chunks = chunk_documents(docs)
    
    # Build vector store
    store = build_vector_store(chunks)
    
    # Test search
    print("\n--- Testing Search ---")
    query = "What are the famous places in Jaipur?"
    results = store.search(query, n_results=3)
    
    print(f"\nQuery: {query}")
    print(f"Found {len(results)} relevant chunks:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. Source: {result['source']}")
        print(f"   Content: {result['content'][:150]}...")
        print()
