# Update main.py to serve the web interface
@"
import os
from adk.python import run_agent_server
from agent import root_agent

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Enable web interface
    run_agent_server(
        root_agent, 
        port=port, 
        host="0.0.0.0",
        serve_web_interface=True
    )
"@ | Out-File -FilePath "main.py" -Encoding utf8 -Force