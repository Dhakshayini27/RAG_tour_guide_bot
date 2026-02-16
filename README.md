<<<<<<< HEAD
# 🗺️ Tour Guide RAG Bot

A simple RAG (Retrieval Augmented Generation) chatbot that answers questions about tourist destinations using your own documents.

## 🎯 What This Project Does

1. **Loads** text documents about tourist places
2. **Chunks** them into smaller pieces for better retrieval
3. **Embeds** them using sentence transformers (runs locally)
4. **Stores** embeddings in ChromaDB vector database
5. **Retrieves** relevant context when you ask questions
6. **Generates** answers using Groq's Llama 3.1 LLM (free API)

## 📁 Project Structure

```
tour-guide-bot/
│
├── data/                       # Your text documents go here
│   ├── jaipur.txt             # Sample document included
│   ├── goa.txt                # Add your own!
│   └── kerala.txt             # Add your own!
│
├── src/                        # Source code
│   ├── load_docs.py           # Load text files
│   ├── chunk_docs.py          # Split into chunks
│   ├── embed_store.py         # Create embeddings & vector store
│   └── query.py               # RAG query system
│
├── .env                        # API keys (create this!)
├── .env.example               # Template for .env
├── .gitignore                 # Git ignore file
├── requirements.txt           # Python dependencies
├── main.py                    # Run this to start!
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `groq` - LLM API (free!)
- `sentence-transformers` - For embeddings (runs locally)
- `chromadb` - Vector database
- `python-dotenv` - For environment variables

### 2. Get Your Free API Key

1. Go to [console.groq.com](https://console.groq.com/)
2. Sign up (it's free!)
3. Create an API key
4. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```
5. Add your API key to `.env`:
   ```
   GROQ_API_KEY=your_actual_api_key_here
   ```

### 3. Add Your Documents

Put `.txt` files in the `data/` directory. I've included a Jaipur sample.

You can:
- Use the Kyoto documents I created earlier
- Create your own documents about any destination
- Download travel guides and save as .txt

### 4. Run the Bot!

```bash
python main.py
```

First time will take a minute to:
- Load the embedding model (downloads ~80MB)
- Process your documents
- Build the vector database

Then you can start chatting!

```
You: What are the famous places in Jaipur?
Bot: [Answer based on your documents]

You: Tell me about the food
Bot: [Answer about food]

You: quit
```

## 🔧 How It Works

### The RAG Pipeline

```
User Question
    ↓
1. Convert question to embedding (vector)
    ↓
2. Search vector database for similar chunks
    ↓
3. Retrieve top 3 most relevant chunks
    ↓
4. Create prompt: context + question
    ↓
5. Send to Groq (Llama 3.1)
    ↓
6. Get answer
    ↓
Display to user
```

### File-by-File Explanation

**load_docs.py**
- Reads all `.txt` files from `data/` directory
- Returns list of documents with source and content

**chunk_docs.py**
- Splits long documents into ~500 character chunks
- Uses 50 character overlap between chunks for context
- Preserves source information for each chunk

**embed_store.py**
- Uses `sentence-transformers` to convert text to vectors
- Stores in ChromaDB (persists to disk in `chroma_db/`)
- Provides search functionality

**query.py**
- Takes user question
- Searches vector store for relevant chunks
- Creates prompt with context
- Calls Groq API with Llama 3.1
- Returns answer

**main.py**
- Entry point that ties everything together
- Handles setup and initialization
- Starts interactive chat

## 💡 Customization Options

### Change Chunk Size

In `main.py`, modify:
```python
chunks = chunk_documents(docs, chunk_size=500, overlap=50)
```

Smaller chunks = more precise but less context
Larger chunks = more context but less precise

### Change Number of Retrieved Chunks

In `query.py`, modify:
```python
def ask(self, query: str, n_results: int = 3):
```

More results = more context but slower and more tokens used

### Change LLM Model

In `query.py`, change:
```python
self.model = "llama-3.1-8b-instant"  # Fast
# or
self.model = "llama-3.1-70b-versatile"  # More powerful
```

Available Groq models:
- `llama-3.1-8b-instant` (fastest, good quality)
- `llama-3.1-70b-versatile` (slower, better quality)
- `mixtral-8x7b-32768` (alternative)

### Change Embedding Model

In `embed_store.py`, change:
```python
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
# or
self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # Better but slower
```

### Rebuild Database

If you add new documents or change chunking:
```bash
python main.py --rebuild
```

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
- Make sure you created `.env` file (not `.env.example`)
- Check the API key is correct
- No quotes needed around the key in `.env`

### "No .txt files found in 'data'"
- Add some `.txt` files to the `data/` directory
- Check file extensions are `.txt` not `.TXT`

### Slow first run
- First run downloads the embedding model (~80MB)
- Subsequent runs are much faster
- Model is cached locally

### Out of memory
- Reduce chunk_size
- Process fewer documents
- Use smaller embedding model

## 📚 Learning Resources

**Understanding Embeddings:**
- Embeddings convert text to numbers (vectors)
- Similar meaning = similar vectors
- We use cosine similarity to find relevant chunks

**Understanding Vector Databases:**
- Store embeddings for fast similarity search
- ChromaDB persists to disk so you don't rebuild each time
- Alternative: FAISS, Pinecone, Weaviate

**Understanding RAG:**
- Retrieval: Find relevant info from your docs
- Augmented: Add this info to the prompt
- Generation: LLM generates answer using the context

## 🎓 Next Steps to Learn

1. **Add more documents** - Try different destinations
2. **Experiment with chunk sizes** - See how it affects answers
3. **Try different models** - Compare Llama 8B vs 70B
4. **Add conversation history** - Make it remember previous questions
5. **Build a web interface** - Use Streamlit or Gradio
6. **Add image support** - Describe places with images
7. **Fine-tune response style** - Make it more formal/casual

## 🤝 Contributing

This is a learning project! Feel free to:
- Add more sample documents
- Improve the code
- Add new features
- Share with others learning RAG

## 📝 License

Free to use for learning and personal projects!

## 🙋 Questions?

Common questions:

**Q: Is this really free?**
A: Yes! Groq API is free, embeddings run locally, ChromaDB is free.

**Q: Can I use OpenAI instead?**
A: Yes! Just change the client in `query.py` to use OpenAI API. But it costs money.

**Q: How many documents can I add?**
A: Hundreds of .txt files should work fine on a normal laptop.

**Q: Can I deploy this?**
A: Yes! Deploy on Streamlit Cloud, Heroku, or any platform that supports Python.

---

**Happy Learning! 🚀**

If you found this helpful, ⭐ star this project!
=======
# RAG_tour_guide_bot
>>>>>>> c838871ce9a371b1c468e2c5ede34c3e4a590bf4
