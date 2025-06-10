#!/usr/bin/env python3
"""
Clean up existing agent deployment before deploying the new full RAG version.
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

# Existing agent resource name
EXISTING_AGENT_RESOURCE_NAME = "projects/442235900540/locations/us-central1/reasoningEngines/6606895002561806336"

def initialize_vertex_ai():
    """Initialize Vertex AI with project settings."""
    print(f"Initializing Vertex AI...")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )
    print("✓ Vertex AI initialized successfully")

def cleanup_existing_agent():
    """Clean up the existing simplified agent deployment."""
    print("\n" + "="*50)
    print("CLEANING UP EXISTING AGENT DEPLOYMENT")
    print("="*50)
    
    print(f"Existing agent resource: {EXISTING_AGENT_RESOURCE_NAME}")
    
    try:
        # Get the existing remote app
        print("Connecting to existing agent...")
        remote_app = agent_engines.get(EXISTING_AGENT_RESOURCE_NAME)
        print("✓ Connected to existing agent")
        
        # Delete the existing agent
        print("Deleting existing agent...")
        remote_app.delete(force=True)
        print("✓ Existing agent deleted successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up existing agent: {str(e)}")
        print("This might be okay if the agent was already deleted or doesn't exist.")
        print("Continuing with deployment...")
        return False

def main():
    """Main cleanup workflow."""
    try:
        # Initialize Vertex AI
        initialize_vertex_ai()
        
        # Ask user for confirmation
        confirm = input(f"\nAre you sure you want to delete the existing agent?\nResource: {EXISTING_AGENT_RESOURCE_NAME}\n(y/n): ")
        if confirm.lower() != 'y':
            print("Cleanup cancelled by user.")
            return False
        
        # Clean up existing agent
        success = cleanup_existing_agent()
        
        if success:
            print("\n" + "="*50)
            print("CLEANUP SUCCESSFUL!")
            print("="*50)
            print("The existing simplified agent has been deleted.")
            print("You can now proceed to deploy the new full RAG agent:")
            print("python deploy_agent_fixed.py")
        else:
            print("\n" + "="*50)
            print("CLEANUP COMPLETED WITH WARNINGS")
            print("="*50)
            print("There were some issues during cleanup, but you can still proceed.")
            print("You can now deploy the new full RAG agent:")
            print("python deploy_agent_fixed.py")
        
        return success
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main() 