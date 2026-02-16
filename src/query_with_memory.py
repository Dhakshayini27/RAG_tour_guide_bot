"""
Query the RAG system and get answers using LLM with conversation memory.
"""
import os
from typing import List, Dict
from dotenv import load_dotenv
from groq import Groq


class TourGuideBot:
    """RAG-based tour guide chatbot with conversation memory."""
    
    def __init__(self, vector_store):
        """
        Initialize the tour guide bot.
        
        Args:
            vector_store: VectorStore instance with loaded documents
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize Groq client
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found! "
                "Create a .env file with your API key from https://console.groq.com/"
            )
        
        self.client = Groq(api_key=api_key)
        self.vector_store = vector_store
        self.model = "llama-3.1-8b-instant"  # Fast and free
        
        # NEW: Conversation memory
        self.conversation_history = []
        self.current_destination = None  # Track current destination being discussed
        
        print("✓ Tour Guide Bot initialized with Groq LLM (with memory)")
    
    def create_prompt(self, query: str, context_chunks: List[Dict], 
                     conversation_history: List[Dict]) -> str:
        """
        Create a prompt with retrieved context and conversation history.
        
        Args:
            query: User's current question
            context_chunks: Relevant chunks from vector store
            conversation_history: Previous conversation turns
            
        Returns:
            Formatted prompt string
        """
        # Combine context from chunks
        context = "\n\n".join([
            f"[From {chunk['source']}]\n{chunk['content']}" 
            for chunk in context_chunks
        ])
        
        # Build conversation history string
        history_text = ""
        if conversation_history:
            history_text = "\nPREVIOUS CONVERSATION:\n"
            for turn in conversation_history[-6:]:  # Keep last 3 exchanges (6 messages)
                role = turn['role'].upper()
                content = turn['content']
                history_text += f"{role}: {content}\n"
            history_text += "\n"
        
        # Create prompt with both context and history
        prompt = f"""You are a helpful tour guide assistant. Use the following information and conversation history to answer the user's question.

IMPORTANT INSTRUCTIONS:
- Remember the destination the user is asking about from the conversation history
- If the user asks follow-up questions (like "hotel suggestions?"), refer to the destination mentioned earlier
- If context doesn't have information about the current destination, politely say so
- Stay consistent with the conversation flow
- Be helpful, friendly, and remember what was discussed before

CONTEXT FROM DOCUMENTS:
{context}
{history_text}
CURRENT USER QUESTION: {query}

ANSWER (be helpful, friendly, and maintain conversation context):"""
        
        return prompt
    
    def ask(self, query: str, n_results: int = 3, verbose: bool = False) -> str:
        """
        Ask a question and get an answer with conversation memory.
        
        Args:
            query: User's question
            n_results: Number of chunks to retrieve
            verbose: Print debugging information
            
        Returns:
            Answer string
        """
        # 1. Extract destination hint from query or history
        destination_hint = self._extract_destination_hint(query)
        
        # 2. Create search query (combine with destination if known)
        search_query = query
        if destination_hint:
            search_query = f"{destination_hint} {query}"
            if verbose:
                print(f"🔍 Enhanced search: {search_query}")
        
        # 3. Retrieve relevant chunks
        if verbose:
            print(f"\n🔍 Searching for relevant information...")
        
        context_chunks = self.vector_store.search(search_query, n_results=n_results)
        
        if verbose:
            print(f"✓ Found {len(context_chunks)} relevant chunks")
            for i, chunk in enumerate(context_chunks, 1):
                print(f"  {i}. {chunk['source']} (chunk {chunk['chunk_id']})")
        
        # 4. Create prompt with context and conversation history
        prompt = self.create_prompt(query, context_chunks, self.conversation_history)
        
        if verbose:
            print(f"\n📝 Prompt length: {len(prompt)} characters")
        
        # 5. Get answer from LLM
        if verbose:
            print(f"🤖 Asking Llama 3.1...")
        
        try:
            # Build messages with history
            messages = [
                {
                    "role": "system",
                    "content": "You are a knowledgeable and friendly tour guide assistant. Remember the conversation context and maintain consistency across questions."
                }
            ]
            
            # Add conversation history (last 3 exchanges)
            for turn in self.conversation_history[-6:]:
                messages.append({
                    "role": turn['role'],
                    "content": turn['content']
                })
            
            # Add current query with context
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # 6. Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": query
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": answer
            })
            
            # 7. Update current destination if mentioned
            new_destination = self._extract_destination_from_answer(query, answer, context_chunks)
            if new_destination:
                self.current_destination = new_destination
                if verbose:
                    print(f"📍 Tracking destination: {self.current_destination}")
            
            if verbose:
                print(f"✓ Got response ({len(answer)} characters)\n")
            
            return answer
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _extract_destination_hint(self, query: str) -> str:
        """
        Extract destination from query or conversation history.
        
        Args:
            query: User's current question
            
        Returns:
            Destination name or empty string
        """
        # Check if user mentioned a destination in current query
        query_lower = query.lower()
        
        # Common city names in our documents
        cities = ['varanasi', 'bengaluru', 'bangalore', 'jaipur', 'hassan', 
                  'kyoto', 'goa', 'delhi', 'mumbai']
        
        for city in cities:
            if city in query_lower:
                return city.title()
        
        # If not in current query, use tracked destination
        if self.current_destination:
            return self.current_destination
        
        # Check recent conversation history
        for turn in reversed(self.conversation_history[-4:]):
            if turn['role'] == 'user':
                for city in cities:
                    if city in turn['content'].lower():
                        return city.title()
        
        return ""
    
    def _extract_destination_from_answer(self, query: str, answer: str, 
                                        context_chunks: List[Dict]) -> str:
        """
        Extract destination from context chunks.
        
        Args:
            query: User's question
            answer: Bot's answer
            context_chunks: Retrieved chunks
            
        Returns:
            Destination name or empty string
        """
        # Get most common source in retrieved chunks
        if not context_chunks:
            return ""
        
        # Count sources
        source_counts = {}
        for chunk in context_chunks:
            source = chunk['source'].lower()
            # Extract city name from filename
            for city in ['varanasi', 'bengaluru', 'bangalore', 'jaipur', 
                        'hassan', 'kyoto', 'goa', 'delhi', 'mumbai']:
                if city in source:
                    source_counts[city.title()] = source_counts.get(city.title(), 0) + 1
        
        # Return most common
        if source_counts:
            return max(source_counts, key=source_counts.get)
        
        return ""
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.current_destination = None
        print("🗑️  Conversation history cleared")
    
    def chat(self):
        """Interactive chat loop with memory."""
        print("\n" + "="*60)
        print("🗺️  TOUR GUIDE BOT - Ask me anything about your destination!")
        print("="*60)
        print("Type 'quit' or 'exit' to end the conversation.")
        print("Type 'clear' to start a new conversation.\n")
        
        while True:
            # Get user input
            query = input("You: ").strip()
            
            # Check for exit
            if query.lower() in ['quit', 'exit', 'bye']:
                print("\nBot: Have a great trip! Goodbye! 👋")
                break
            
            # Check for clear
            if query.lower() == 'clear':
                self.clear_history()
                print("\nBot: Starting fresh! What would you like to know?\n")
                continue
            
            # Skip empty queries
            if not query:
                continue
            
            # Get and print answer
            answer = self.ask(query, verbose=False)
            print(f"\nBot: {answer}\n")


if __name__ == "__main__":
    # Test the bot
    from load_docs import load_documents
    from chunk_docs import chunk_documents
    from embed_store import VectorStore
    
    print("Setting up Tour Guide Bot...\n")
    
    # Load documents
    docs = load_documents()
    
    # Chunk documents
    chunks = chunk_documents(docs)
    
    # Create/load vector store
    store = VectorStore()
    
    # Check if we need to add documents
    if store.collection.count() == 0:
        print("\nFirst time setup - adding documents to vector store...")
        store.add_documents(chunks)
    else:
        print(f"\nUsing existing vector store with {store.collection.count()} chunks")
    
    # Initialize bot
    bot = TourGuideBot(store)
    
    # Start chat
    bot.chat()
