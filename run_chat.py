#!/usr/bin/env python3
"""
Run the Streamlit chat interface for the RAG Agent.
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit chat interface."""
    print("🤖 Starting RAG Agent Chat Interface...")
    print("This will open a web browser with the chat interface.")
    print("Press Ctrl+C to stop the server.")
    print()
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_chat.py",
            "--server.port=8501",
            "--server.address=localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Chat interface stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main() 