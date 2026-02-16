"""
Load and read text documents from the data directory.
"""
import os
from typing import List, Dict


def load_documents(data_dir: str = "data") -> List[Dict[str, str]]:
    """
    Load all .txt files from the data directory.
    
    Args:
        data_dir: Path to directory containing text files
        
    Returns:
        List of dictionaries with 'source' and 'content' keys
    """
    documents = []
    
    # Check if directory exists
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory '{data_dir}' not found!")
    
    # Get all .txt files
    txt_files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
    
    if not txt_files:
        raise ValueError(f"No .txt files found in '{data_dir}'")
    
    print(f"Found {len(txt_files)} document(s) to load...")
    
    # Read each file
    for filename in txt_files:
        filepath = os.path.join(data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            documents.append({
                'source': filename,
                'content': content
            })
            
            print(f"✓ Loaded {filename} ({len(content)} characters)")
            
        except Exception as e:
            print(f"✗ Error loading {filename}: {e}")
            continue
    
    print(f"\nTotal documents loaded: {len(documents)}")
    return documents


if __name__ == "__main__":
    # Test the function
    docs = load_documents()
    
    # Print summary
    for doc in docs:
        print(f"\nFile: {doc['source']}")
        print(f"Preview: {doc['content'][:200]}...")
