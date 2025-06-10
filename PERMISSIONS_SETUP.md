# Agent Engine Permissions Setup

You've encountered the common permission error when deploying to Vertex AI Agent Engine. This guide will help you set up the required permissions.

## Quick Fix - Run the Setup Script

First, try the automated setup script:

```bash
python setup_permissions.py
```

This script will:
1. Get your project number
2. Enable required APIs
3. Check/create your staging bucket
4. Grant the necessary IAM roles to the Agent Engine service account

## Manual Setup (if script fails)

If the automated script doesn't work, follow these manual steps:

### 1. Get Your Project Number

```bash
gcloud projects describe gen-lang-client-0516570023 --format="value(projectNumber)"
```

Save this number - you'll need it for the next step.

### 2. Enable Required APIs

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable storage.googleapis.com
```

### 3. Grant IAM Roles

Replace `YOUR_PROJECT_NUMBER` with the number from step 1:

```bash
# Storage Admin role
gcloud projects add-iam-policy-binding gen-lang-client-0516570023 \
    --member="serviceAccount:service-YOUR_PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# AI Platform User role
gcloud projects add-iam-policy-binding gen-lang-client-0516570023 \
    --member="serviceAccount:service-442235900540@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Artifact Registry Reader role
gcloud projects add-iam-policy-binding gen-lang-client-0516570023 \
    --member="serviceAccount:service-442235900540@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.reader"

# Cloud Build Builder role
gcloud projects add-iam-policy-binding gen-lang-client-0516570023 \
    --member="serviceAccount:service-442235900540@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"
```

### 4. Verify Staging Bucket

Make sure your staging bucket exists and is accessible:

```bash
gsutil ls gs://rag-agent-bucket-hmk
```

If it doesn't exist, create it:

```bash
gsutil mb -p gen-lang-client-0516570023 gs://rag-agent-bucket-hmk
```

## Example with Actual Project Number

If your project number is `123456789`, the commands would look like:

```bash
gcloud projects add-iam-policy-binding gen-lang-client-0516570023 \
    --member="serviceAccount:service-123456789@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding gen-lang-client-0516570023 \
    --member="serviceAccount:service-123456789@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding gen-lang-client-0516570023 \
    --member="serviceAccount:service-123456789@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.reader"

gcloud projects add-iam-policy-binding gen-lang-client-0516570023 \
    --member="serviceAccount:service-123456789@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"
```

## After Setting Up Permissions

Once you've set up the permissions, retry the deployment:

```bash
python deploy_agent.py
```

## Troubleshooting

### Permission Denied Errors
- Make sure you have Owner or Editor role on the project
- Verify you're authenticated: `gcloud auth list`
- Check your project: `gcloud config get-value project`

### API Not Enabled Errors
- Run the enable commands above
- Wait a few minutes for APIs to fully activate

### Bucket Access Errors
- Verify the bucket name in your `.env` file
- Check bucket permissions: `gsutil iam get gs://rag-agent-bucket-hmk`

### Still Having Issues?
- Check the Google Cloud Console IAM page to verify the service account has the roles
- Look at Cloud Logging for more detailed error messages
- Verify your quotas in the Google Cloud Console

## What These Permissions Do

- **Storage Admin**: Allows Agent Engine to store deployment artifacts in your bucket
- **AI Platform User**: Enables using Vertex AI services
- **Artifact Registry Reader**: Allows reading container images during deployment
- **Cloud Build Builder**: Enables building the agent container during deployment 