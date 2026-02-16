"""
Split documents into smaller chunks for better retrieval.
"""
from typing import List, Dict


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text to split
        chunk_size: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        # Get chunk
        end = start + chunk_size
        chunk = text[start:end]
        
        # If not the last chunk, try to break at sentence or word boundary
        if end < len(text):
            # Try to find last period, question mark, or exclamation
            last_sentence = max(
                chunk.rfind('. '),
                chunk.rfind('? '),
                chunk.rfind('! '),
                chunk.rfind('\n\n')
            )
            
            if last_sentence > chunk_size // 2:  # Only if we find a break point past halfway
                chunk = chunk[:last_sentence + 1]
                end = start + last_sentence + 1
        
        chunks.append(chunk.strip())
        start = end - overlap  # Overlap for context
    
    return chunks


def chunk_documents(documents: List[Dict[str, str]], 
                    chunk_size: int = 500, 
                    overlap: int = 50) -> List[Dict[str, str]]:
    """
    Chunk multiple documents while preserving source information.
    
    Args:
        documents: List of docs with 'source' and 'content'
        chunk_size: Maximum characters per chunk
        overlap: Number of characters to overlap
        
    Returns:
        List of chunks with source metadata
    """
    all_chunks = []
    
    print(f"Chunking documents (chunk_size={chunk_size}, overlap={overlap})...")
    
    for doc in documents:
        source = doc['source']
        content = doc['content']
        
        # Split into chunks
        chunks = chunk_text(content, chunk_size, overlap)
        
        # Add metadata to each chunk
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                'content': chunk,
                'source': source,
                'chunk_id': i
            })
        
        print(f"✓ {source}: {len(chunks)} chunks")
    
    print(f"\nTotal chunks created: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    # Test the chunking
    from load_docs import load_documents
    
    # Load documents
    docs = load_documents()
    
    # Chunk them
    chunks = chunk_documents(docs, chunk_size=500, overlap=50)
    
    # Show sample
    print("\n--- Sample Chunk ---")
    print(f"Source: {chunks[0]['source']}")
    print(f"Chunk ID: {chunks[0]['chunk_id']}")
    print(f"Content: {chunks[0]['content'][:200]}...")
