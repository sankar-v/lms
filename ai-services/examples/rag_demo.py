"""
Example script demonstrating RAG pipeline usage.

This script shows how to:
1. Ingest documents
2. Search for information
3. Manage documents

Run: python examples/rag_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import IngestionOrchestrator
from src.embeddings import EmbeddingService
from src.vector_store.client import VectorStoreClient


async def demo_ingestion():
    """Demonstrate document ingestion."""
    print("\n" + "="*60)
    print("DEMO 1: Document Ingestion")
    print("="*60)
    
    orchestrator = IngestionOrchestrator(
        chunk_size=1000,
        chunk_overlap=200,
        embedding_batch_size=50
    )
    
    # Create a sample document
    sample_doc = Path("sample_doc.md")
    sample_doc.write_text("""
# Sample Documentation

## Introduction
This is a sample document for the RAG pipeline demo.

## Features
Our system provides:
- Document ingestion from multiple formats
- Semantic search capabilities
- Efficient vector storage with PostgreSQL

## Getting Started
To get started with the system:
1. Install dependencies
2. Configure your environment
3. Start the services

## FAQ

### How do I deploy?
Deployment is handled through Docker Compose. Run `docker-compose up` to start.

### What file formats are supported?
We support PDF, Markdown, Text, HTML, and DOCX files.
""")
    
    try:
        # Ingest the document
        print("\n📄 Ingesting sample document...")
        task = await orchestrator.ingest_document(
            str(sample_doc),
            metadata_overrides={
                "category": "documentation",
                "tags": ["sample", "demo"]
            }
        )
        
        print(f"✅ Status: {task.status.value}")
        print(f"   Document ID: {task.document_id if hasattr(task, 'document_id') else 'N/A'}")
        print(f"   Chunks created: {task.processed_chunks}")
        print(f"   Progress: {task.progress_percentage:.1f}%")
        
        # Get stats
        stats = orchestrator.get_stats()
        print(f"\n📊 Pipeline Stats:")
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Completed tasks: {stats['completed_tasks']}")
        
    finally:
        # Cleanup
        sample_doc.unlink(missing_ok=True)
        await orchestrator.close()


async def demo_search():
    """Demonstrate semantic search."""
    print("\n" + "="*60)
    print("DEMO 2: Semantic Search")
    print("="*60)
    
    embedding_service = EmbeddingService()
    vector_store = VectorStoreClient()
    
    try:
        # Search query
        query = "How do I deploy the application?"
        print(f"\n🔍 Searching for: '{query}'")
        
        # Generate embedding
        query_embedding = await embedding_service.embed(query)
        print(f"   Generated embedding: {len(query_embedding)} dimensions")
        
        # Search
        results = await vector_store.search(
            query_embedding=query_embedding,
            top_k=3,
            threshold=0.5
        )
        
        if results:
            print(f"\n✅ Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. Score: {result['score']:.3f}")
                print(f"   Source: {result['source']}")
                print(f"   Content: {result['text'][:150]}...")
                print()
        else:
            print("\n❌ No results found. Try ingesting some documents first.")
            print("   Run: python -m src.cli ingest ../docs --pattern '*.md'")
        
    finally:
        await embedding_service.close()


async def demo_document_management():
    """Demonstrate document management."""
    print("\n" + "="*60)
    print("DEMO 3: Document Management")
    print("="*60)
    
    vector_store = VectorStoreClient()
    
    # List documents
    print("\n📚 Listing documents...")
    docs = vector_store.list_documents(limit=10)
    
    if docs:
        print(f"\nFound {len(docs)} documents:\n")
        for i, doc in enumerate(docs, 1):
            print(f"{i}. {doc['source']}")
            print(f"   ID: {doc['document_id']}")
            
            # Get detailed info
            info = vector_store.get_document_info(doc['document_id'])
            if info:
                print(f"   Chunks: {info['chunk_count']}")
                if info.get('metadata', {}).get('category'):
                    print(f"   Category: {info['metadata']['category']}")
            print()
    else:
        print("\n❌ No documents found. Ingest some documents first.")
    
    # Show stats
    total = vector_store.get_document_count()
    print(f"📊 Total chunks in vector store: {total}")


async def demo_sdk_usage():
    """Demonstrate SDK usage patterns."""
    print("\n" + "="*60)
    print("DEMO 4: SDK Usage Patterns")
    print("="*60)
    
    print("""
The RAG pipeline can be used in three ways:

1. Python SDK (Programmatic):
   ```python
   from src.ingestion import IngestionOrchestrator
   orchestrator = IngestionOrchestrator()
   task = await orchestrator.ingest_document("file.pdf")
   ```

2. CLI Tool (Command-line):
   ```bash
   python -m src.cli ingest docs/ --pattern "*.md"
   python -m src.cli search "deployment guide"
   ```

3. REST API (HTTP):
   ```bash
   curl -X POST http://localhost:8001/documents/upload \\
        -F "file=@guide.pdf"
   ```

Each mode provides the same functionality - choose based on your use case!
""")


async def main():
    """Run all demos."""
    print("\n" + "🚀 RAG Pipeline Demo" + "\n")
    
    try:
        await demo_ingestion()
        await demo_search()
        await demo_document_management()
        await demo_sdk_usage()
        
        print("\n" + "="*60)
        print("✅ Demo completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Ingest your documents: python -m src.cli ingest <path>")
        print("2. Search: python -m src.cli search '<query>'")
        print("3. Start API: uvicorn main:app --reload")
        print("4. View API docs: http://localhost:8001/docs")
        print()
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running: docker-compose up postgres")
        print("2. Check your .env file has OPENAI_API_KEY")
        print("3. Verify DATABASE_URL is correct")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
