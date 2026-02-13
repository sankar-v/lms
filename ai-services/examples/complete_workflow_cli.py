#!/usr/bin/env python3
"""
Complete workflow demonstration: Upload → Embed → Store → Retrieve
This script demonstrates the full RAG pipeline using the CLI approach.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import IngestionOrchestrator
from src.rag.retriever import DocumentRetriever
from src.rag.generator import AnswerGenerator
from src.vector_store.client import VectorStoreClient
from langchain_openai import ChatOpenAI
from src.config import settings


async def run_complete_workflow():
    """Run the complete RAG workflow."""
    
    print("=" * 80)
    print("RAG PIPELINE COMPLETE WORKFLOW DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Step 1: Initialize components
    print("📦 Step 1: Initializing components...")
    orchestrator = IngestionOrchestrator()
    retriever = DocumentRetriever()
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        openai_api_key=settings.OPENAI_API_KEY
    )
    generator = AnswerGenerator(llm)
    vector_store = VectorStoreClient()
    print("✅ Components initialized")
    print()
    
    # Step 2: Upload and process document
    print("📄 Step 2: Uploading and processing document...")
    test_doc = Path(__file__).parent.parent / "test_data" / "engineering_best_practices.md"
    
    if not test_doc.exists():
        print(f"❌ Test document not found: {test_doc}")
        return
    
    print(f"   Document: {test_doc.name}")
    
    # Ingest the document
    result = await orchestrator.ingest_document(
        file_path=str(test_doc),
        metadata_overrides={
            "category": "best-practices",
            "tags": ["engineering", "platform", "guidelines"]
        }
    )
    
    print(f"✅ Document processed:")
    print(f"   - Task ID: {result.task_id}")
    print(f"   - Total chunks: {result.total_chunks}")
    print(f"   - Status: {result.status}")
    print()
    
    # Step 3: Verify storage
    print("💾 Step 3: Verifying storage...")
    doc_count = vector_store.get_document_count()
    print(f"✅ Vector store stats:")
    print(f"   - Total documents: {doc_count}")
    print()
    
    # Step 4: Retrieve relevant documents
    print("🔍 Step 4: Testing document retrieval...")
    
    test_queries = [
        "What are the microservices design principles?",
        "How should we handle secrets and credentials?",
        "What are the Kubernetes best practices?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: '{query}'")
        print("   " + "-" * 70)
        
        # Retrieve relevant chunks
        results = await retriever.retrieve(query, top_k=3)
        
        if results:
            print(f"   ✅ Found {len(results)} relevant chunks:")
            for j, result in enumerate(results, 1):
                print(f"      {j}. Score: {result['score']:.3f}")
                print(f"         Preview: {result['text'][:100]}...")
                print(f"         Source: {result.get('source', 'unknown')}")
        else:
            print("   ⚠️  No results found")
    
    print()
    
    # Step 5: Generate answer using RAG
    print("🤖 Step 5: Generating AI-powered answer...")
    query = "What security practices should we follow for authentication and data protection?"
    print(f"   Question: '{query}'")
    print("   " + "-" * 70)
    
    # Retrieve context
    context_chunks = await retriever.retrieve(query, top_k=5)
    
    if context_chunks:
        # Generate answer
        context_text = "\n\n".join([chunk['text'] for chunk in context_chunks])
        result = await generator.generate(
            question=query,
            context=context_chunks,
            history=[],
            system_prompt="""You are a helpful AI assistant for an engineering platform.
Answer questions based on the provided documentation. Be concise and accurate."""
        )
        
        print(f"\n   📝 Generated Answer:")
        print(f"   {result['text']}")
        print()
        
        print(f"   📊 Confidence: {result['confidence']:.2f}")
        print()
        
        # Show sources
        print(f"   📚 Sources: {', '.join(result['sources'])}")
    else:
        print("   ⚠️  Could not generate answer - no relevant context found")
    
    print()
    print("=" * 80)
    print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
    print("=" * 80)


async def cleanup():
    """Optional cleanup function."""
    print("\n🧹 Cleanup (optional)...")
    # You can add cleanup logic here if needed
    print("   Skipping cleanup - documents remain in database")


if __name__ == "__main__":
    try:
        asyncio.run(run_complete_workflow())
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
