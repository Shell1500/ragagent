#!/usr/bin/env python3
"""
Setup IAM permissions for Vertex AI Agent Engine deployment.

This script helps you set up the required permissions for the Agent Engine service account.
"""

import os
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0516570023")

def get_project_number():
    """Get the Google Cloud project number."""
    try:
        result = subprocess.run([
            "gcloud", "projects", "describe", PROJECT_ID, "--format=value(projectNumber)"
        ], capture_output=True, text=True, check=True)
        project_number = result.stdout.strip()
        print(f"✓ Project number: {project_number}")
        return project_number
    except subprocess.CalledProcessError as e:
        print(f"Error getting project number: {e}")
        return None

def setup_agent_engine_permissions(project_number):
    """Set up the required permissions for Agent Engine service account."""
    
    service_account = f"service-{project_number}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
    
    print(f"\nSetting up permissions for service account: {service_account}")
    
    # Required roles for Agent Engine
    required_roles = [
        "roles/storage.admin",
        "roles/aiplatform.user",
        "roles/artifactregistry.reader",
        "roles/cloudbuild.builds.builder"
    ]
    
    print("\nGranting required roles...")
    
    for role in required_roles:
        try:
            cmd = [
                "gcloud", "projects", "add-iam-policy-binding", PROJECT_ID,
                "--member", f"serviceAccount:{service_account}",
                "--role", role
            ]
            
            print(f"Granting role: {role}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ Successfully granted {role}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error granting {role}: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    return True

def enable_required_apis():
    """Enable required APIs for Agent Engine."""
    
    required_apis = [
        "aiplatform.googleapis.com",
        "cloudbuild.googleapis.com",
        "artifactregistry.googleapis.com",
        "storage.googleapis.com"
    ]
    
    print("\nEnabling required APIs...")
    
    for api in required_apis:
        try:
            cmd = ["gcloud", "services", "enable", api]
            print(f"Enabling API: {api}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ Successfully enabled {api}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error enabling {api}: {e}")
            return False
    
    return True

def check_bucket_permissions():
    """Check if the staging bucket exists and has proper permissions."""
    staging_bucket = os.environ.get("GOOGLE_CLOUD_STAGING_BUCKET", "gs://rag-agent-bucket-hmk")
    bucket_name = staging_bucket.replace("gs://", "")
    
    print(f"\nChecking staging bucket: {staging_bucket}")
    
    # Check if bucket exists
    try:
        cmd = ["gsutil", "ls", "-b", staging_bucket]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Bucket {staging_bucket} exists")
    except subprocess.CalledProcessError:
        print(f"❌ Bucket {staging_bucket} does not exist or is not accessible")
        print(f"Creating bucket...")
        try:
            cmd = ["gsutil", "mb", "-p", PROJECT_ID, staging_bucket]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ Created bucket {staging_bucket}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating bucket: {e}")
            return False
    
    return True

def main():
    """Main setup workflow."""
    print("=" * 60)
    print("SETTING UP VERTEX AI AGENT ENGINE PERMISSIONS")
    print("=" * 60)
    print(f"Project ID: {PROJECT_ID}")
    
    # Step 1: Get project number
    print("\n1. Getting project number...")
    project_number = get_project_number()
    if not project_number:
        print("❌ Failed to get project number. Exiting.")
        return
    
    # Step 2: Enable required APIs
    print("\n2. Enabling required APIs...")
    if not enable_required_apis():
        print("❌ Failed to enable some APIs. You may need to enable them manually.")
    
    # Step 3: Check/create staging bucket
    print("\n3. Checking staging bucket...")
    if not check_bucket_permissions():
        print("❌ Bucket setup failed. Please check manually.")
    
    # Step 4: Set up service account permissions
    print("\n4. Setting up service account permissions...")
    if setup_agent_engine_permissions(project_number):
        print("\n✓ All permissions set up successfully!")
        print("\nYou can now retry the deployment with:")
        print("python deploy_agent.py")
    else:
        print("\n❌ Permission setup failed.")
        print("\nYou may need to run these commands manually:")
        service_account = f"service-{project_number}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
        print(f"\nManual commands:")
        print(f"gcloud projects add-iam-policy-binding {PROJECT_ID} --member='serviceAccount:{service_account}' --role='roles/storage.admin'")
        print(f"gcloud projects add-iam-policy-binding {PROJECT_ID} --member='serviceAccount:{service_account}' --role='roles/aiplatform.user'")
        print(f"gcloud projects add-iam-policy-binding {PROJECT_ID} --member='serviceAccount:{service_account}' --role='roles/artifactregistry.reader'")
        print(f"gcloud projects add-iam-policy-binding {PROJECT_ID} --member='serviceAccount:{service_account}' --role='roles/cloudbuild.builds.builder'")

if __name__ == "__main__":
    main() 