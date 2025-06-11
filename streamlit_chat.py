import streamlit as st
import os
import sys
import ast
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines
from google.oauth2 import service_account


# Load environment variables
load_dotenv()

# Configuration
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0516570023")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("GOOGLE_CLOUD_STAGING_BUCKET", "gs://rag-agent-bucket-hmk")
AGENT_RESOURCE_NAME = "projects/442235900540/locations/us-central1/reasoningEngines/6196856330238558208"

@st.cache_resource
def initialize_vertex_ai():
    """Initialize Vertex AI."""
    
    if "gcp_service_account" in st.secrets:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
    else:
        creds = None   # falls back to local ADC if you’re on your laptop

    # 2️⃣ init Vertex AI
    vertexai.init(
        project        = PROJECT_ID,
        location       = LOCATION,
        staging_bucket = STAGING_BUCKET,
        credentials    = creds,
    )
    return agent_engines.get(AGENT_RESOURCE_NAME, credentials=creds)

def create_chat_session(_remote_app):
    """Create a new chat session."""
    return _remote_app.create_session(user_id="streamlit_user")

def send_query(remote_app, session_id, message):
    """Send a query and get the parsed text response."""
    try:
        response_stream = remote_app.stream_query(
            user_id="streamlit_user",
            session_id=session_id,
            message=message,
        )
        
        text_response = ""
        for event_str in response_stream:
            try:
                event = ast.literal_eval(str(event_str))
                if isinstance(event, dict) and 'content' in event and 'parts' in event['content']:
                    for part in event['content']['parts']:
                        if 'text' in part:
                            text_response += part['text']
            except (ValueError, SyntaxError):
                continue
        
        return text_response if text_response else "No text response found."

    except Exception as e:
        return f"Error: {str(e)}"

# --- Streamlit App ---

st.set_page_config(page_title="RAG Agent Chat", page_icon="🏗️")
st.title("🏗️ Construction Project RAG Agent")

# Initialize agent
try:
    remote_app = initialize_vertex_ai()
except Exception as e:
    st.error(f"Failed to initialize agent: {e}")
    st.stop()

# Initialize session state
if "session_id" not in st.session_state:
    with st.spinner("Creating new chat session..."):
        session = create_chat_session(remote_app)
        st.session_state.session_id = session["id"]
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you with the project documents today?"}]

# New Chat button
if st.sidebar.button("New Chat"):
    with st.spinner("Starting new chat..."):
        session = create_chat_session(remote_app)
        st.session_state.session_id = session["id"]
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you with the project documents today?"}]
    st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            response = send_query(remote_app, st.session_state.session_id, prompt)
            st.markdown(response)
    
    # Add agent response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
