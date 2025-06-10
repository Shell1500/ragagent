#!/usr/bin/env python3
"""
Interactive CLI chat with the deployed RAG Agent.
"""

import os
import sys
import ast
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines

# Load environment variables
load_dotenv()

# Configuration from environment variables
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0516570023")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("GOOGLE_CLOUD_STAGING_BUCKET", "gs://rag-agent-bucket-hmk")

# Resource name from successful deployment
AGENT_RESOURCE_NAME = "projects/442235900540/locations/us-central1/reasoningEngines/6196856330238558208"
def initialize_vertex_ai():
    """Initialize Vertex AI with project settings."""
    print("Initializing Vertex AI...")
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )
    print("✓ Vertex AI initialized")

def get_deployed_agent():
    """Get the deployed agent using its resource name."""
    try:
        print("Connecting to deployed RAG agent...")
        remote_app = agent_engines.get(AGENT_RESOURCE_NAME)
        print("✓ Connected to deployed agent successfully")
        return remote_app
    except Exception as e:
        print(f"❌ Failed to connect to agent: {str(e)}")
        sys.exit(1)

def create_chat_session(remote_app):
    """Create a new chat session."""
    try:
        print("Creating new chat session...")
        session = remote_app.create_session(user_id="interactive_user")
        print(f"✓ Chat session created: {session['id']}")
        return session
    except Exception as e:
        print(f"❌ Failed to create session: {str(e)}")
        sys.exit(1)

def send_query(remote_app, session_id, message):
    """Send a query to the agent and get the response."""
    try:
        print("\n🤖 Agent is thinking...")
        response_stream = remote_app.stream_query(
            user_id="interactive_user",
            session_id=session_id,
            message=message,
        )
        
        text_response = ""
        for event_str in response_stream:
            try:
                # Convert the string representation of the event to a dictionary
                event = ast.literal_eval(str(event_str))
                
                # Check if the event has the expected structure
                if isinstance(event, dict) and 'content' in event and 'parts' in event['content']:
                    for part in event['content']['parts']:
                        if 'text' in part:
                            text_response += part['text']
            except (ValueError, SyntaxError):
                # Handle cases where the string is not a valid literal
                continue
        
        return text_response if text_response else "No text response found."

    except Exception as e:
        return f"❌ Error getting response: {str(e)}"

def print_welcome():
    """Print welcome message and instructions."""
    print("\n" + "="*60)
    print("🏗️  CONSTRUCTION PROJECT RAG AGENT - INTERACTIVE CHAT")
    print("="*60)
    print("Welcome! You're now connected to your RAG agent with full access")
    print("to all construction project documentation.")
    print("\nAvailable capabilities:")
    print("• Search through project documents")
    print("• Add new documents to the corpus")
    print("• Get corpus information")
    print("• Delete documents")
    print("\nCommands:")
    print("• Type your questions naturally")
    print("• Type 'help' for sample queries")
    print("• Type 'info' to get corpus information")
    print("• Type 'quit' or 'exit' to end the session")
    print("\n" + "="*60)

def print_help():
    """Print help with sample queries."""
    print("\n📚 SAMPLE QUERIES:")
    print("="*40)
    print("• 'What documents do you have access to?'")
    print("• 'Search for safety protocols'")
    print("• 'Find information about concrete specifications'")
    print("• 'What are the project deadlines?'")
    print("• 'Show me contract details'")
    print("• 'Add this document: https://drive.google.com/file/d/your-file-id'")
    print("• 'Get corpus information'")
    print("="*40)

def main():
    """Main interactive chat loop."""
    try:
        # Initialize and connect
        initialize_vertex_ai()
        remote_app = get_deployed_agent()
        session = create_chat_session(remote_app)
        
        # Print welcome
        print_welcome()
        
        # Interactive chat loop
        session_id = session["id"]
        
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Chat session ended.")
                    break
                elif user_input.lower() == 'help':
                    print_help()
                    continue
                elif user_input.lower() == 'info':
                    user_input = "Get corpus information"
                elif not user_input:
                    print("Please enter a message or type 'help' for examples.")
                    continue
                
                # Send query to agent
                response = send_query(remote_app, session_id, user_input)
                
                # Display response
                print(f"\n🤖 Agent: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error in chat loop: {str(e)}")
                continue
                
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
