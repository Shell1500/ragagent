#!/usr/bin/env python3
"""
Manage deployed RAG Agent on Vertex AI Agent Engine.

This script helps you interact with and manage your deployed agent.
"""

import os
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines

# Load environment variables
load_dotenv()

# Configuration from environment variables
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0516570023")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("GOOGLE_CLOUD_STAGING_BUCKET", "gs://rag-agent-bucket-hmk")

def initialize_vertex_ai():
    """Initialize Vertex AI with project settings."""
    print(f"Initializing Vertex AI...")
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )
    print("✓ Vertex AI initialized successfully")

def get_agent_by_resource_name(resource_name):
    """Get an existing deployed agent by its resource name."""
    try:
        # This would typically be done by reconstructing the agent object
        # You'll need to replace this with the actual resource name from your deployment
        print(f"Connecting to agent: {resource_name}")
        # Note: You may need to use a different method to reconnect to existing agents
        # This is a placeholder - check the actual Agent Engine documentation for reconnection
        return None
    except Exception as e:
        print(f"Error connecting to agent: {str(e)}")
        return None

def test_agent_queries(remote_app):
    """Test various queries on the deployed agent."""
    print("\n" + "="*50)
    print("TESTING AGENT QUERIES")
    print("="*50)
    
    # Create a session for testing
    test_session = remote_app.create_session(user_id="test_manager")
    session_id = test_session["id"]
    
    # Test queries
    test_queries = [
        "What documents are available in the corpus?",
        "Get corpus information",
        "What types of documents are in the project?",
        "How many documents are in the corpus?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i}: {query} ---")
        try:
            for event in remote_app.stream_query(
                user_id="test_manager",
                session_id=session_id,
                message=query,
            ):
                print(f"Response: {event}")
        except Exception as e:
            print(f"Error with query: {str(e)}")
        print("-" * 40)

def interactive_chat(remote_app):
    """Start an interactive chat session with the deployed agent."""
    print("\n" + "="*50)
    print("INTERACTIVE CHAT MODE")
    print("="*50)
    print("Type 'quit' to exit the chat session")
    
    # Create a session for interactive chat
    chat_session = remote_app.create_session(user_id="interactive_user")
    session_id = chat_session["id"]
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        print("Agent: ", end="")
        try:
            for event in remote_app.stream_query(
                user_id="interactive_user",
                session_id=session_id,
                message=user_input,
            ):
                # Extract text from the event if it contains a text response
                if isinstance(event, dict) and 'parts' in event:
                    for part in event['parts']:
                        if 'text' in part:
                            print(part['text'], end="")
        except Exception as e:
            print(f"Error: {str(e)}")
        print()  # New line after response

def cleanup_agent(remote_app):
    """Clean up the deployed agent resources."""
    print("\n" + "="*50)
    print("CLEANUP RESOURCES")
    print("="*50)
    
    confirm = input("Are you sure you want to delete the deployed agent? This cannot be undone. (yes/no): ")
    
    if confirm.lower() == 'yes':
        try:
            print("Deleting deployed agent...")
            remote_app.delete(force=True)
            print("✓ Agent and all associated resources deleted successfully")
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
    else:
        print("Cleanup cancelled.")

def main():
    """Main management interface."""
    initialize_vertex_ai()
    
    print("\n" + "="*50)
    print("RAG AGENT MANAGEMENT INTERFACE")
    print("="*50)
    
    # You'll need to replace this with your actual deployed agent's resource name
    resource_name = input("Enter your deployed agent's resource name (from deployment): ").strip()
    
    if not resource_name:
        print("Error: Resource name is required")
        return
    
    # Note: You may need to adjust this based on how Agent Engine handles reconnection
    # This is a simplified example
    print(f"Note: You'll need to implement agent reconnection logic for resource: {resource_name}")
    print("For now, you can use the remote_app object returned from your deployment script.")
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Test agent with sample queries")
        print("2. Interactive chat with agent")
        print("3. Cleanup/delete agent")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            print("To test queries, you need to pass the remote_app object from your deployment.")
            # test_agent_queries(remote_app)
        elif choice == '2':
            print("To start interactive chat, you need to pass the remote_app object from your deployment.")
            # interactive_chat(remote_app)
        elif choice == '3':
            print("To cleanup, you need to pass the remote_app object from your deployment.")
            # cleanup_agent(remote_app)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 