#!/usr/bin/env python3
"""
Deploy the RAG Agent to Vertex AI Agent Engine.

This script deploys the existing RAG agent to Google Cloud Vertex AI Agent Engine
for production use.
"""

import os
from dotenv import load_dotenv
import vertexai
from vertexai.preview import reasoning_engines
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
    print(f"Project ID: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Staging Bucket: {STAGING_BUCKET}")
    
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )
    print("✓ Vertex AI initialized successfully")

def create_deployable_app():
    """Create a deployable app from the RAG agent."""
    from rag_agent.agent import root_agent
    
    print("Creating deployable app from RAG agent...")
    
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )
    
    print("✓ Deployable app created successfully")
    return app

def test_agent_locally(app):
    """Test the agent locally before deployment."""
    print("\nTesting agent locally...")
    
    # Create a test session
    session = app.create_session(user_id="test_user")
    print(f"✓ Local session created: {session.id}")
    
    # Test a simple query
    print("\nTesting query: 'What documents are available in the corpus?'")
    
    for event in app.stream_query(
        user_id="test_user",
        session_id=session.id,
        message="What documents are available in the corpus?",
    ):
        print(f"Event: {event}")
    
    print("✓ Local testing completed")
    return session

def deploy_to_agent_engine():
    """Deploy the agent to Vertex AI Agent Engine."""
    from rag_agent.agent import root_agent
    
    print("\n" + "="*50)
    print("DEPLOYING TO VERTEX AI AGENT ENGINE")
    print("="*50)
    
    print("Starting deployment to Agent Engine...")
    print("⚠️  This step may take several minutes to complete...")
    
    # Include all requirements that your agent needs
    requirements = [
        "google-cloud-aiplatform[adk,agent_engines]",
        "google-cloud-storage",
        "python-dotenv",
        "google-adk",
        "google-genai",
        "gitpython",
        "requests",
        "sseclient-py",
    ]
    
    print("Requirements being deployed:", requirements)
    
    remote_app = agent_engines.create(
        agent_engine=root_agent,
        requirements=requirements,
        # Include the current directory so rag_agent module can be found
        extra_packages=["./rag_agent"]
    )
    
    print("✓ Agent deployed successfully to Agent Engine!")
    print(f"Resource name: {remote_app.resource_name}")
    
    return remote_app

def test_remote_agent(remote_app):
    """Test the deployed agent remotely."""
    print("\nTesting deployed agent...")
    
    # Create a remote session
    remote_session = remote_app.create_session(user_id="test_user_remote")
    print(f"✓ Remote session created: {remote_session['id']}")
    
    # Test a query on the remote agent
    print("\nTesting remote query: 'What documents are available in the corpus?'")
    
    for event in remote_app.stream_query(
        user_id="test_user_remote",
        session_id=remote_session["id"],
        message="What documents are available in the corpus?",
    ):
        print(f"Remote event: {event}")
    
    print("✓ Remote testing completed")
    return remote_session

def main():
    """Main deployment workflow."""
    try:
        # Initialize Vertex AI
        initialize_vertex_ai()
        
        # Create deployable app
        app = create_deployable_app()
        
        # Test locally first
        print("\n" + "="*50)
        print("LOCAL TESTING")
        print("="*50)
        local_session = test_agent_locally(app)
        
        # Ask user if they want to proceed with deployment
        proceed = input("\nLocal testing completed. Proceed with deployment to Agent Engine? (y/n): ")
        if proceed.lower() != 'y':
            print("Deployment cancelled by user.")
            return
        
        # Deploy to Agent Engine
        remote_app = deploy_to_agent_engine()
        
        # Test remote deployment
        print("\n" + "="*50)
        print("REMOTE TESTING")
        print("="*50)
        remote_session = test_remote_agent(remote_app)
        
        # Success message
        print("\n" + "="*50)
        print("DEPLOYMENT SUCCESSFUL!")
        print("="*50)
        print(f"Your RAG agent is now deployed to Vertex AI Agent Engine.")
        print(f"Resource name: {remote_app.resource_name}")
        print(f"You can now interact with your agent using the remote_app object.")
        print("\nTo clean up resources later, run:")
        print("remote_app.delete(force=True)")
        
    except Exception as e:
        print(f"❌ Error during deployment: {str(e)}")
        raise

if __name__ == "__main__":
    main() 