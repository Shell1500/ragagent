# RAG Agent Deployment to Vertex AI Agent Engine

This guide will help you deploy your existing RAG agent to Google Cloud Vertex AI Agent Engine.

## Prerequisites

1. **Google Cloud Project**: Ensure you have a Google Cloud project with:
   - Vertex AI API enabled
   - Agent Engine API enabled
   - Proper IAM permissions (Vertex AI User, Storage Admin)

2. **Environment Variables**: Your `.env` file should contain:
   ```
   GOOGLE_CLOUD_PROJECT="gen-lang-client-0516570023"
   GOOGLE_CLOUD_LOCATION="us-central1"
   GOOGLE_GENAI_USE_VERTEXAI="True"
   GOOGLE_CLOUD_STAGING_BUCKET="gs://rag-agent-bucket-hmk"
   ```

3. **Dependencies**: Your `requirements.txt` already includes the necessary packages:
   - `google-cloud-aiplatform[adk,agent_engines]`
   - `google-cloud-storage`
   - `python-dotenv`

## Deployment Steps

### 1. Activate Your Virtual Environment
```bash
# Activate your virtual environment (adjust path as needed)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Authenticate with Google Cloud
```bash
# Authenticate with your Google Cloud account
gcloud auth login

# Set your project
gcloud config set project gen-lang-client-0516570023

# Generate application default credentials
gcloud auth application-default login
```

### 4. Run the Deployment Script
```bash
python deploy_agent.py
```

The deployment script will:
1. Initialize Vertex AI with your project settings
2. Create a deployable app from your RAG agent
3. Test the agent locally first
4. Ask for confirmation before deploying
5. Deploy to Vertex AI Agent Engine
6. Test the deployed agent remotely
7. Provide you with the resource name for future management

### 5. Expected Output

During deployment, you'll see output like:
```
Initializing Vertex AI...
Project ID: gen-lang-client-0516570023
Location: us-central1
Staging Bucket: gs://rag-agent-bucket-hmk
✓ Vertex AI initialized successfully

Creating deployable app from RAG agent...
✓ Deployable app created successfully

==================================================
LOCAL TESTING
==================================================
Testing agent locally...
✓ Local session created: [session-id]
...

Local testing completed. Proceed with deployment to Agent Engine? (y/n): y

==================================================
DEPLOYING TO VERTEX AI AGENT ENGINE
==================================================
Starting deployment to Agent Engine...
⚠️  This step may take several minutes to complete...
✓ Agent deployed successfully to Agent Engine!
Resource name: projects/[PROJECT]/locations/us-central1/reasoningEngines/[RESOURCE_ID]

==================================================
DEPLOYMENT SUCCESSFUL!
==================================================
```

### 6. Save Your Resource Name

**Important**: Save the resource name provided at the end of deployment. You'll need it to:
- Reconnect to your deployed agent
- Manage and test your agent
- Clean up resources later

Example resource name format:
```
projects/123456789/locations/us-central1/reasoningEngines/987654321
```

## Testing Your Deployed Agent

After deployment, you can interact with your agent using the `remote_app` object returned by the deployment script.

### Create a Session
```python
# Create a session with your deployed agent
session = remote_app.create_session(user_id="your_user_id")
```

### Send Queries
```python
# Send queries to your deployed agent
for event in remote_app.stream_query(
    user_id="your_user_id",
    session_id=session["id"],
    message="What documents are available in the corpus?",
):
    print(event)
```

## Managing Your Deployed Agent

Use the `manage_agent.py` script to interact with your deployed agent:

```bash
python manage_agent.py
```

This script provides options to:
1. Test agent with sample queries
2. Start an interactive chat session
3. Clean up/delete the agent

## Cost Considerations

- Agent Engine charges based on usage (queries, compute time)
- The staging bucket will store deployment artifacts
- Consider setting up billing alerts

## Cleanup

To avoid ongoing charges, delete your deployed agent when no longer needed:

```python
# In your Python script or interactive session
remote_app.delete(force=True)
```

Or use the management script option 3.

## Troubleshooting

### Common Issues

1. **Authentication Error**: 
   - Run `gcloud auth application-default login`
   - Verify your Google Cloud project permissions

2. **Staging Bucket Access**:
   - Ensure the bucket exists: `gsutil ls gs://rag-agent-bucket-hmk`
   - Verify write permissions to the bucket

3. **API Not Enabled**:
   - Enable Vertex AI API: `gcloud services enable aiplatform.googleapis.com`
   - Enable required APIs in Google Cloud Console

4. **Timeout During Deployment**:
   - Agent Engine deployment can take 10-15 minutes
   - Be patient and don't interrupt the process

### Getting Help

- Check the [Vertex AI Agent Engine documentation](https://cloud.google.com/vertex-ai/docs/agent-engine)
- Review Google Cloud logs in the Console
- Verify your environment variables are correctly set

## Security Notes

- Your `.env` file contains sensitive information - keep it secure
- Use IAM best practices (principle of least privilege)
- Regularly review and audit deployed resources
- Consider using Google Cloud Secret Manager for production deployments 