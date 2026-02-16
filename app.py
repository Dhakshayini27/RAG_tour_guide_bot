import streamlit as st
from src.query_with_memory import TourGuideBot
from src.embed_store import VectorStore

st.set_page_config(page_title="RAG Tour Guide Bot", page_icon="🌍", layout="wide")

# Initialize vector store & bot ONCE using session state
if "bot" not in st.session_state:
    with st.spinner("Loading tour guide bot..."):
        store = VectorStore()
        st.session_state.bot = TourGuideBot(store)

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Get bot from session state
bot = st.session_state.bot

# Title
st.title("🗺️ Your Tour Guide Bot")
st.markdown("Ask me anything about your travel destination!")

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.write("This RAG-powered chatbot helps you plan your trips.")
    st.write("It remembers our conversation, so feel free to ask follow-up questions!")
    
    st.markdown("---")
    
    # Show current destination being tracked
    if bot.current_destination:
        st.success(f"📍 Currently discussing: **{bot.current_destination}**")
    else:
        st.info("💡 Mention a destination to get started!")
    
    st.markdown("---")
    
    # Stats
    st.metric("Messages", len(st.session_state.history))
    st.metric("Conversations", len(bot.conversation_history) // 2)
    
    st.markdown("---")
    
    # Clear button in sidebar
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.history = []
        bot.clear_history()
        st.rerun()

# Display chat messages
chat_container = st.container()

with chat_container:
    for message in st.session_state.history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant", avatar="🗺️"):
                st.write(message["content"])

# Chat input at bottom
user_input = st.chat_input("Ask about hotels, food, attractions, or anything else...")

# Process input
if user_input:
    # Add user message to history
    st.session_state.history.append({"role": "user", "content": user_input})
    
    # Display user message immediately
    with st.chat_message("user"):
        st.write(user_input)
    
    # Get bot response
    with st.chat_message("assistant", avatar="🗺️"):
        with st.spinner("Thinking..."):
            response = bot.ask(user_input, verbose=False)
        st.write(response)
    
    # Add assistant response to history
    st.session_state.history.append({"role": "assistant", "content": response})
    
    # Force rerun to update sidebar stats
    st.rerun()