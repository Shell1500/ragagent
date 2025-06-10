#!/usr/bin/env python3
"""
Deploy the RAG Agent to Vertex AI Agent Engine (Standalone Version).

This version includes all configuration directly without external module dependencies.
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

def create_standalone_rag_agent():
    """Create the standalone RAG agent with all dependencies included."""
    
    print("Creating standalone RAG agent for deployment...")
    
    from google.adk.agents import Agent
    from typing import List
    
    # Import the standalone RAG functionality
    def rag_query_tool(query: str) -> dict:
        """Standalone RAG query tool with all configuration included."""
        try:
            from vertexai import rag
            
            # Configuration constants (included directly)
            DEFAULT_TOP_K = 10
            DEFAULT_DISTANCE_THRESHOLD = 0.7
            
            # Use the hardcoded corpus resource name
            corpus_resource_name = "projects/gen-lang-client-0516570023/locations/us-central1/ragCorpora/4532873024948404224"
            
            # Configure retrieval parameters
            rag_retrieval_config = rag.RagRetrievalConfig(
                top_k=DEFAULT_TOP_K,
                filter=rag.Filter(vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD),
            )

            # Perform the query
            print(f"Performing RAG query: {query}")
            response = rag.retrieval_query(
                rag_resources=[
                    rag.RagResource(
                        rag_corpus=corpus_resource_name,
                    )
                ],
                text=query,
                rag_retrieval_config=rag_retrieval_config,
            )

            # Process the response into a more usable format
            results = []
            if hasattr(response, "contexts") and response.contexts:
                for ctx_group in response.contexts.contexts:
                    result = {
                        "source_uri": (
                            ctx_group.source_uri if hasattr(ctx_group, "source_uri") else ""
                        ),
                        "source_name": (
                            ctx_group.source_display_name
                            if hasattr(ctx_group, "source_display_name")
                            else ""
                        ),
                        "text": ctx_group.text if hasattr(ctx_group, "text") else "",
                        "score": ctx_group.score if hasattr(ctx_group, "score") else 0.0,
                    }
                    results.append(result)

            # If we didn't find any results
            if not results:
                return {
                    "status": "warning",
                    "message": f"No results found in corpus for query: '{query}'",
                    "query": query,
                    "corpus_name": "test",
                    "results": [],
                    "results_count": 0,
                }

            return {
                "status": "success",
                "message": f"Successfully queried corpus",
                "query": query,
                "corpus_name": "test",
                "results": results,
                "results_count": len(results),
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error querying corpus: {str(e)}",
                "query": query,
                "corpus_name": "test",
            }
    
    def get_corpus_info_tool() -> dict:
        """Get corpus information standalone."""
        try:
            from vertexai import rag
            
            # Use the hardcoded corpus resource name
            corpus_resource_name = "projects/gen-lang-client-0516570023/locations/us-central1/ragCorpora/4532873024948404224"
            
            # Process file information
            file_details = []
            try:
                # Get the list of files
                files = rag.list_files(corpus_resource_name)
                for rag_file in files:
                    try:
                        # Extract the file ID from the name
                        file_id = rag_file.name.split("/")[-1]

                        file_info = {
                            "file_id": file_id,
                            "display_name": (
                                rag_file.display_name
                                if hasattr(rag_file, "display_name")
                                else ""
                            ),
                            "source_uri": (
                                rag_file.source_uri
                                if hasattr(rag_file, "source_uri")
                                else ""
                            ),
                            "create_time": (
                                str(rag_file.create_time)
                                if hasattr(rag_file, "create_time")
                                else ""
                            ),
                            "update_time": (
                                str(rag_file.update_time)
                                if hasattr(rag_file, "update_time")
                                else ""
                            ),
                        }

                        file_details.append(file_info)
                    except Exception:
                        # Continue to the next file
                        continue
            except Exception:
                # Continue without file details
                pass

            return {
                "status": "success",
                "message": f"Successfully retrieved corpus information",
                "corpus_name": "test",
                "corpus_display_name": "test",
                "file_count": len(file_details),
                "files": file_details,
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error getting corpus information: {str(e)}",
                "corpus_name": "test",
            }
    
    def add_data_tool(paths: List[str]) -> dict:
        """Add data to the corpus standalone."""
        try:
            from vertexai import rag
            import re
            
            # Configuration constants (included directly)
            DEFAULT_CHUNK_SIZE = 512
            DEFAULT_CHUNK_OVERLAP = 100
            DEFAULT_EMBEDDING_REQUESTS_PER_MIN = 1000
            PROJECT_ID_CONST = "gen-lang-client-0516570023"
            LOCATION_CONST = "us-central1"
            
            # Validate inputs
            if not paths or not all(isinstance(path, str) for path in paths):
                return {
                    "status": "error",
                    "message": "Invalid paths: Please provide a list of URLs or GCS paths",
                    "corpus_name": "test",
                    "paths": paths,
                }

            # Pre-process paths to validate and convert Google Docs URLs
            validated_paths = []
            invalid_paths = []
            conversions = []
            
            for path in paths:
                path = path.strip()
                if not path:
                    continue
                    
                # Check if it's a Google Docs/Sheets/Slides URL that needs conversion
                docs_match = re.search(r'https://docs\.google\.com/(?:document|spreadsheets|presentation)/d/([a-zA-Z0-9-_]+)', path)
                if docs_match:
                    file_id = docs_match.group(1)
                    drive_url = f"https://drive.google.com/file/d/{file_id}/view"
                    validated_paths.append(drive_url)
                    conversions.append({"original": path, "converted": drive_url})
                    continue
                
                # Check if it's already a proper Google Drive URL
                if re.match(r'https://drive\.google\.com/file/d/[a-zA-Z0-9-_]+', path):
                    validated_paths.append(path)
                    continue
                
                # Check if it's a GCS path
                if path.startswith('gs://'):
                    validated_paths.append(path)
                    continue
                
                # If none of the above, it's invalid
                invalid_paths.append(path)

            if not validated_paths:
                return {
                    "status": "error",
                    "message": "No valid paths provided",
                    "corpus_name": "test",
                    "paths": paths,
                    "invalid_paths": invalid_paths,
                }

            # Use the hardcoded corpus resource name
            corpus_resource_name = "projects/gen-lang-client-0516570023/locations/us-central1/ragCorpora/4532873024948404224"
            
            # Set up chunking configuration
            transformation_config = rag.TransformationConfig(
                chunking_config=rag.ChunkingConfig(
                    chunk_size=DEFAULT_CHUNK_SIZE,
                    chunk_overlap=DEFAULT_CHUNK_OVERLAP,
                ),
            )
            
            # Set up LLM parser configuration
            MODEL_ID = "gemini-2.0-flash"
            MODEL_NAME = f"projects/{PROJECT_ID_CONST}/locations/{LOCATION_CONST}/publishers/google/models/{MODEL_ID}"
            MAX_PARSING_REQUESTS_PER_MIN = 1000
            CUSTOM_PARSING_PROMPT = """
You are an expert document processing assistant specializing in extracting and converting PDF content into clean, structured text suitable for Retrieval-Augmented Generation (RAG) systems.
Your Task
Extract ALL textual content from the provided PDF document and convert it into clean, well-structured plain text that preserves the semantic meaning and logical flow of information.
"""
            
            llm_parser_config = rag.LlmParserConfig(
                model_name=MODEL_NAME,
                max_parsing_requests_per_min=MAX_PARSING_REQUESTS_PER_MIN,
                custom_parsing_prompt=CUSTOM_PARSING_PROMPT,
            )

            # Import files to the corpus
            import_result = rag.import_files(
                corpus_resource_name,
                validated_paths,
                transformation_config=transformation_config,
                llm_parser=llm_parser_config,
                max_embedding_requests_per_min=DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
            )

            # Build the success message
            conversion_msg = ""
            if conversions:
                conversion_msg = " (Converted Google Docs URLs to Drive format)"

            return {
                "status": "success",
                "message": f"Successfully added {import_result.imported_rag_files_count} file(s) to corpus{conversion_msg}",
                "corpus_name": "test",
                "files_added": import_result.imported_rag_files_count,
                "paths": validated_paths,
                "invalid_paths": invalid_paths,
                "conversions": conversions,
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error adding data to corpus: {str(e)}",
                "corpus_name": "test",
                "paths": paths,
            }
    
    def delete_document_tool(document_id: str) -> dict:
        """Delete document standalone."""
        try:
            from vertexai import rag
            
            # Use the hardcoded corpus resource name
            corpus_resource_name = "projects/gen-lang-client-0516570023/locations/us-central1/ragCorpora/4532873024948404224"
            
            # Delete the document
            rag_file_path = f"{corpus_resource_name}/ragFiles/{document_id}"
            rag.delete_file(rag_file_path)

            return {
                "status": "success",
                "message": f"Successfully deleted document '{document_id}' from corpus",
                "corpus_name": "test",
                "document_id": document_id,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error deleting document: {str(e)}",
                "corpus_name": "test",
                "document_id": document_id,
            }
    
    # Create the standalone RAG agent
    standalone_rag_agent = Agent(
        name="HMKAgent_Standalone",
        model="gemini-2.5-flash-preview-04-17",
        description="Vertex AI RAG Agent - Standalone Version",
        tools=[
            rag_query_tool,
            get_corpus_info_tool,
            add_data_tool,
            delete_document_tool,
        ],
        instruction="""
You are an experienced construction project coordinator with comprehensive access to all project documentation, contracts, plans, reports, and site data. Your role is to help project stakeholders quickly find accurate information and make informed decisions.

Your Expertise
You have instant access to the complete project documentation through your document search capabilities. When someone asks a question, you naturally search through the relevant documents to provide accurate, detailed answers. You understand construction terminology, project workflows, safety requirements, compliance issues, and contractual obligations.

How You Work
When responding to questions, you automatically search the project documents to find the most relevant and up-to-date information. If your initial search doesn't provide complete coverage of a topic, you'll perform additional searches with different approaches to ensure you've found all pertinent details.

You're thorough in your research - if someone asks about a contract provision, safety protocol, or technical specification, you'll search comprehensively to provide complete context, including related requirements, deadlines, responsible parties, and any recent updates or changes.

Your Approach
- Be conversational and helpful: Respond naturally, as if you're a knowledgeable team member who happens to have perfect recall of all project documents
- Search comprehensively: Don't settle for partial information. If a question seems complex or multi-faceted, perform multiple searches to gather complete details
- Provide context: When sharing information, include relevant background, implications, and connections to other project elements
- Be precise about sources: When you find information, reference which documents or sections it comes from
- Acknowledge limitations: If you can't find specific information after thorough searching, clearly state that it's not available in the current documentation

Available Information
You can access all project documents. When needed, you can also get detailed information about the document set to better understand what information is available.

Available Tools:
1. rag_query_tool - Query the project document corpus with full RAG functionality
2. get_corpus_info_tool - Get detailed information about the document corpus including file counts and metadata
3. add_data_tool - Add new documents to the corpus with proper processing and chunking
4. delete_document_tool - Delete documents from the corpus

You must be precise and specific in your answers. You can make multiple queries to the corpus to get the information you need. If you think the fetched information is not enough, you can try to fetch additional information from the documents and attempt to search for more relevant information.

Remember: Your goal is to be the most knowledgeable and helpful team member anyone could ask for regarding this construction project. You have access to everything - use that capability to provide comprehensive, accurate answers that help people make better decisions and keep the project moving smoothly.
"""
    )
    
    print("✓ Standalone RAG agent created with all dependencies included")
    return standalone_rag_agent

def deploy_to_agent_engine():
    """Deploy the standalone RAG agent to Vertex AI Agent Engine."""
    
    agent = create_standalone_rag_agent()
    
    print("\n" + "="*50)
    print("DEPLOYING STANDALONE RAG AGENT TO VERTEX AI AGENT ENGINE")
    print("="*50)
    
    print("Starting deployment with standalone RAG functionality...")
    print("⚠️  This step may take several minutes to complete...")
    
    # Include requirements for standalone RAG functionality
    requirements = [
        "google-adk",
        "google-cloud-aiplatform[adk,agent_engines]",
        "google-cloud-storage",
        "google-genai",
        "python-dotenv",
    ]
    
    print("Requirements being deployed:", requirements)
    
    try:
        remote_app = agent_engines.create(
            agent_engine=agent,
            requirements=requirements
        )
        
        print("✓ Standalone RAG Agent deployed successfully to Agent Engine!")
        print(f"Resource name: {remote_app.resource_name}")
        
        return remote_app
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        print("Full error details:")
        import traceback
        traceback.print_exc()
        raise

def test_standalone_rag_agent(remote_app):
    """Test the deployed standalone agent."""
    print("\nTesting deployed standalone agent...")
    
    # Create a remote session
    remote_session = remote_app.create_session(user_id="test_user_standalone")
    print(f"✓ Remote session created: {remote_session['id']}")
    
    # Test queries on the remote agent
    test_queries = [
        "What washing machines did we use on this project?", 
        "Any dob violations on this project?",
        "What is the project budget?",
        "What is the project schedule?"
    ]
    
    for query in test_queries:
        print(f"\nTesting standalone query: '{query}'")
        try:
            response_parts = []
            for event in remote_app.stream_query(
                user_id="test_user_standalone",
                session_id=remote_session["id"],
                message=query,
            ):
                response_parts.append(str(event))
                
            # Print a summary of the response
            print(f"Response received: {len(response_parts)} events")
            if response_parts:
                print(f"Sample response: {response_parts[-1][:300]}...")
                
        except Exception as e:
            print(f"Error with query '{query}': {e}")
    
    print("✓ Standalone testing completed")
    return remote_session

def main():
    """Main deployment workflow for standalone functionality."""
    try:
        # Initialize Vertex AI
        initialize_vertex_ai()
        
        # Ask user if they want to proceed with standalone deployment
        proceed = input("\nProceed with standalone RAG deployment to Agent Engine? (y/n): ")
        if proceed.lower() != 'y':
            print("Deployment cancelled by user.")
            return
        
        # Deploy to Agent Engine with standalone functionality
        remote_app = deploy_to_agent_engine()
        
        # Test remote deployment
        print("\n" + "="*50)
        print("STANDALONE TESTING")
        print("="*50)
        remote_session = test_standalone_rag_agent(remote_app)
        
        # Success message
        print("\n" + "="*50)
        print("STANDALONE DEPLOYMENT SUCCESSFUL!")
        print("="*50)
        print(f"Your standalone RAG agent is now deployed to Vertex AI Agent Engine.")
        print(f"Resource name: {remote_app.resource_name}")
        print("\nStandalone capabilities included:")
        print("✓ Real corpus querying with retrieval")
        print("✓ Document management (add/delete)")
        print("✓ Corpus information access")
        print("✓ All dependencies included")
        print("✓ No external module dependencies")
        print("\nTo interact with your deployed agent, update the resource name in:")
        print("chat_with_agent.py")
        print("\nTo clean up resources later, run:")
        print("remote_app.delete(force=True)")
        
        # Return the remote app for further interaction
        return remote_app
        
    except Exception as e:
        print(f"❌ Error during standalone deployment: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main() 