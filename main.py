"""
Tour Guide RAG Bot - Main Entry Point

This is a simple RAG (Retrieval Augmented Generation) system that:
1. Loads documents about tourist destinations
2. Splits them into chunks
3. Creates embeddings and stores in vector database
4. Answers questions using retrieved context + LLM
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from load_docs import load_documents
from chunk_docs import chunk_documents
from embed_store import VectorStore
from query_with_memory import TourGuideBot


def setup_database(rebuild: bool = False):
    """
    Set up the vector database.
    
    Args:
        rebuild: If True, clear and rebuild the database
    """
    print("="*60)
    print("SETTING UP TOUR GUIDE BOT")
    print("="*60)
    
    # Load documents
    print("\n[1/4] Loading documents...")
    docs = load_documents(data_dir="data")
    
    # Chunk documents
    print("\n[2/4] Chunking documents...")
    chunks = chunk_documents(docs, chunk_size=500, overlap=50)
    
    # Create vector store
    print("\n[3/4] Initializing vector store...")
    store = VectorStore(collection_name="tour_guide")
    
    # Add documents if needed
    if rebuild or store.collection.count() == 0:
        print("\n[4/4] Building vector database...")
        if rebuild and store.collection.count() > 0:
            print("  Clearing existing data...")
            store.clear()
        store.add_documents(chunks)
    else:
        print(f"\n[4/4] Using existing database ({store.collection.count()} chunks)")
    
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE")
    print("="*60)
    
    return store


def main():
    """Main function."""
    # Check for rebuild flag
    rebuild = '--rebuild' in sys.argv
    
    try:
        # Setup database
        store = setup_database(rebuild=rebuild)
        
        # Initialize bot
        print("\nInitializing chatbot...")
        bot = TourGuideBot(store)
        
        # Start interactive chat
        bot.chat()
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have .txt files in the 'data/' directory.")
        print("You can use the Kyoto documents I created earlier or add your own!")
        
    except ValueError as e:
        if "GROQ_API_KEY" in str(e):
            print(f"\n❌ Error: {e}")
            print("\nTo fix this:")
            print("1. Go to https://console.groq.com/")
            print("2. Sign up for free")
            print("3. Get your API key")
            print("4. Create a .env file in this directory")
            print("5. Add: GROQ_API_KEY=your_key_here")
        else:
            print(f"\n❌ Error: {e}")
    
    except KeyboardInterrupt:
        print("\n\nExiting... Goodbye! 👋")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
