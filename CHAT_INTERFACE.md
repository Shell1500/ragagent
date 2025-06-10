# RAG Agent Chat Interface

A simple Streamlit-based chat interface to interact with your deployed Vertex AI RAG Agent.

## Quick Start

1. **Run the chat interface:**
   ```bash
   python run_chat.py
   ```
   
   Or directly with Streamlit:
   ```bash
   streamlit run streamlit_chat.py
   ```

2. **Open your browser** to the displayed URL (usually `http://localhost:8501`)

3. **Start chatting** with your RAG agent!

## Features

- 💬 **Real-time chat interface** with your deployed agent
- 🔄 **Streaming responses** for real-time interaction
- 📱 **Responsive design** that works on desktop and mobile
- 📝 **Chat history** preserved during the session
- 🔧 **Session management** with ability to start new sessions
- ℹ️ **Agent information** displayed in the sidebar

## Agent Information

- **Resource Name:** `projects/442235900540/locations/us-central1/reasoningEngines/1107788751309897728`
- **Project:** gen-lang-client-0516570023
- **Location:** us-central1
- **Version:** Full RAG with corpus functionality

## Available Agent Tools

Your deployed agent has access to these tools:
- 🔍 **RAG Query Tool** - Search through project documents
- 📋 **Get Corpus Info** - Get information about the document corpus
- ➕ **Add Data Tool** - Add new documents to the corpus
- 🗑️ **Delete Document Tool** - Delete documents from the corpus

## Usage Tips

1. **Ask specific questions** about your project documents
2. **Use natural language** - the agent understands conversational queries
3. **Try different approaches** if the first query doesn't give you what you need
4. **Use the sidebar** to clear chat history or start a new session

## Example Queries

- "What is your corpus information?"
- "Can you search for project documents?"
- "What tools do you have available?"
- "Tell me about the project documentation"

## Troubleshooting

If you encounter issues:

1. **Check your environment variables** are set correctly
2. **Ensure you're authenticated** with Google Cloud
3. **Verify the agent is still deployed** at the specified resource name
4. **Check the terminal** for error messages

To stop the interface, press `Ctrl+C` in the terminal.

## Note

This interface connects to your deployed agent with **full RAG functionality**. Your agent now has complete access to:
- Real document corpus querying with retrieval
- Document management (add/delete) with proper processing  
- Corpus information access with file metadata
- Smart chunking and embedding capabilities
- LLM-based document parsing for complex documents 