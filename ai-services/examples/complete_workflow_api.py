#!/usr/bin/env python3
"""
Complete workflow demonstration using REST API
This script demonstrates the full RAG pipeline using HTTP requests to the FastAPI service.

Prerequisites:
1. Start the API server: cd ai-services && python main.py
2. Run this script: python examples/complete_workflow_api.py
"""

import asyncio
import httpx
import time
from pathlib import Path


API_BASE_URL = "http://localhost:8001"


async def run_api_workflow():
    """Run the complete RAG workflow using REST API."""
    
    print("=" * 80)
    print("RAG PIPELINE REST API WORKFLOW DEMONSTRATION")
    print("=" * 80)
    print(f"API Base URL: {API_BASE_URL}")
    print()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Step 1: Check API health
        print("🏥 Step 1: Checking API health...")
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                print("✅ API is healthy")
            else:
                print(f"⚠️  API returned status code: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            print("   Make sure the API server is running: python main.py")
            return
        print()
        
        # Step 2: Upload document
        print("📄 Step 2: Uploading document...")
        test_doc = Path(__file__).parent.parent / "test_data" / "engineering_best_practices.md"
        
        if not test_doc.exists():
            print(f"❌ Test document not found: {test_doc}")
            return
        
        print(f"   Document: {test_doc.name}")
        
        with open(test_doc, "rb") as f:
            files = {"file": (test_doc.name, f, "text/markdown")}
            data = {
                "category": "best-practices",
                "tags": "engineering,platform,guidelines"
            }
            
            response = await client.post(
                f"{API_BASE_URL}/documents/upload",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            upload_result = response.json()
            task_id = upload_result["task_id"]
            print(f"✅ Document uploaded successfully")
            print(f"   - Task ID: {task_id}")
            print(f"   - Status: {upload_result['status']}")
            print(f"   - Message: {upload_result['message']}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   {response.text}")
            return
        print()
        
        # Step 3: Check task status
        print("⏳ Step 3: Monitoring processing status...")
        max_attempts = 10
        for attempt in range(max_attempts):
            response = await client.get(f"{API_BASE_URL}/documents/task/{task_id}")
            
            if response.status_code == 200:
                status_result = response.json()
                status = status_result["status"]
                progress = status_result["progress_percentage"]
                
                print(f"   Attempt {attempt + 1}: Status={status}, Progress={progress:.1f}%")
                
                if status == "completed":
                    print(f"✅ Processing completed!")
                    print(f"   - Total chunks: {status_result['total_chunks']}")
                    print(f"   - Processed chunks: {status_result['processed_chunks']}")
                    break
                elif status == "failed":
                    print(f"❌ Processing failed: {status_result.get('error_message')}")
                    return
                
                await asyncio.sleep(2)
            else:
                print(f"⚠️  Status check failed: {response.status_code}")
        print()
        
        # Step 4: List documents
        print("📚 Step 4: Listing documents in vector store...")
        response = await client.get(f"{API_BASE_URL}/documents/list")
        
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Found {len(documents)} documents:")
            for i, doc in enumerate(documents[:5], 1):  # Show first 5
                print(f"   {i}. {doc['source']} ({doc['chunk_count']} chunks)")
        else:
            print(f"⚠️  List failed: {response.status_code}")
        print()
        
        # Step 5: Search for relevant information
        print("🔍 Step 5: Searching for relevant information...")
        
        test_queries = [
            "What are the microservices design principles?",
            "How should we handle secrets and credentials?",
            "What are the Kubernetes best practices?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Query {i}: '{query}'")
            print("   " + "-" * 70)
            
            response = await client.post(
                f"{API_BASE_URL}/documents/search",
                json={
                    "query": query,
                    "top_k": 3,
                    "threshold": 0.7
                }
            )
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    print(f"   ✅ Found {len(results)} relevant chunks:")
                    for j, result in enumerate(results, 1):
                        print(f"      {j}. Score: {result['score']:.3f}")
                        print(f"         Preview: {result['content'][:100]}...")
                        print(f"         Source: {result['metadata'].get('source', 'unknown')}")
                else:
                    print("   ⚠️  No results found")
            else:
                print(f"   ❌ Search failed: {response.status_code}")
        
        print()
        
        # Step 6: Get AI-powered answer via chat
        print("🤖 Step 6: Getting AI-powered answer...")
        question = "What security practices should we follow for authentication and data protection?"
        print(f"   Question: '{question}'")
        print("   " + "-" * 70)
        
        response = await client.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": question,
                "history": []
            }
        )
        
        if response.status_code == 200:
            chat_result = response.json()
            print(f"\n   📝 AI Response:")
            print(f"   {chat_result['response']}")
            print()
            
            if 'sources' in chat_result and chat_result['sources']:
                print(f"   📚 Sources used:")
                for source in chat_result['sources']:
                    print(f"      - {source}")
        else:
            print(f"   ❌ Chat failed: {response.status_code}")
        
        print()
        print("=" * 80)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(run_api_workflow())
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
