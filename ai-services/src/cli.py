#!/usr/bin/env python3
"""
CLI tool for RAG document management.

Usage:
    python -m src.cli ingest <file_or_directory> [options]
    python -m src.cli list [options]
    python -m src.cli delete <document_id>
    python -m src.cli search <query> [options]
    python -m src.cli stats
"""

import asyncio
import sys
import argparse
import json
import logging
from pathlib import Path
from typing import Optional

from .ingestion import IngestionOrchestrator
from .embeddings import EmbeddingService
from .vector_store.client import VectorStoreClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGCLI:
    """RAG pipeline CLI."""
    
    def __init__(self):
        self.orchestrator = IngestionOrchestrator()
        self.vector_store = VectorStoreClient()
        self.embedding_service = EmbeddingService()
    
    async def ingest(
        self,
        path: str,
        recursive: bool = True,
        pattern: str = "*.*",
        category: Optional[str] = None,
        tags: Optional[list] = None,
    ):
        """Ingest documents from file or directory."""
        path_obj = Path(path)
        
        metadata_overrides = {}
        if category:
            metadata_overrides["category"] = category
        if tags:
            metadata_overrides["tags"] = tags
        
        try:
            if path_obj.is_file():
                print(f"📄 Ingesting file: {path}")
                task = await self.orchestrator.ingest_document(
                    path,
                    metadata_overrides=metadata_overrides,
                )
                self._print_task_result(task)
                
            elif path_obj.is_dir():
                print(f"📁 Ingesting directory: {path}")
                print(f"   Pattern: {pattern}, Recursive: {recursive}")
                tasks = await self.orchestrator.ingest_directory(
                    path,
                    pattern=pattern,
                    recursive=recursive,
                    metadata_overrides=metadata_overrides,
                )
                
                print(f"\n✅ Completed: {len(tasks)} documents ingested")
                for task in tasks:
                    print(f"   - {Path(task.document_path).name}: {task.processed_chunks} chunks")
            else:
                print(f"❌ Error: Path not found: {path}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Ingestion failed", exc_info=True)
            sys.exit(1)
    
    def list_documents(self, limit: int = 50, offset: int = 0):
        """List documents in vector store."""
        try:
            docs = self.vector_store.list_documents(limit=limit, offset=offset)
            total = self.vector_store.get_document_count()
            
            print(f"\n📚 Documents in vector store: {total} total\n")
            
            for i, doc in enumerate(docs, start=offset + 1):
                print(f"{i}. {doc['source']}")
                print(f"   ID: {doc['document_id']}")
                print(f"   Created: {doc['created_at']}")
                if doc.get('metadata'):
                    metadata = doc['metadata']
                    if isinstance(metadata, dict):
                        if metadata.get('category'):
                            print(f"   Category: {metadata['category']}")
                        if metadata.get('tags'):
                            print(f"   Tags: {', '.join(metadata['tags'])}")
                print()
            
        except Exception as e:
            print(f"❌ Error listing documents: {e}")
            sys.exit(1)
    
    def get_info(self, document_id: str):
        """Get information about a specific document."""
        try:
            info = self.vector_store.get_document_info(document_id)
            
            if not info:
                print(f"❌ Document not found: {document_id}")
                sys.exit(1)
            
            print(f"\n📄 Document Information\n")
            print(f"ID: {info['document_id']}")
            print(f"Source: {info['source']}")
            print(f"Chunks: {info['chunk_count']}")
            print(f"Created: {info['created_at']}")
            
            if info.get('metadata'):
                print(f"\nMetadata:")
                print(json.dumps(info['metadata'], indent=2))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def delete(self, document_id: str):
        """Delete a document."""
        try:
            count = self.vector_store.delete_by_document_id(document_id)
            
            if count > 0:
                print(f"✅ Deleted document {document_id} ({count} chunks)")
            else:
                print(f"❌ Document not found: {document_id}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def delete_by_source(self, source: str):
        """Delete documents by source path."""
        try:
            count = self.vector_store.delete_by_source(source)
            
            if count > 0:
                print(f"✅ Deleted {count} chunks from source: {source}")
            else:
                print(f"❌ No documents found for source: {source}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    async def search(self, query: str, top_k: int = 5, threshold: float = 0.7):
        """Search for documents."""
        try:
            print(f"🔍 Searching for: '{query}'\n")
            
            # Generate query embedding
            query_embedding = await self.embedding_service.embed(query)
            
            # Search
            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                threshold=threshold,
            )
            
            if not results:
                print("No results found.")
                return
            
            print(f"Found {len(results)} results:\n")
            
            for i, result in enumerate(results, 1):
                print(f"{i}. Score: {result['score']:.3f}")
                print(f"   Source: {result['source']}")
                print(f"   Content: {result['text'][:200]}...")
                print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error("Search failed", exc_info=True)
            sys.exit(1)
    
    def stats(self):
        """Show statistics."""
        try:
            stats = self.orchestrator.get_stats()
            
            print("\n📊 RAG Pipeline Statistics\n")
            print(f"Total Documents: {stats['total_documents']}")
            print(f"Total Tasks: {stats['total_tasks']}")
            print(f"  - Completed: {stats['completed_tasks']}")
            print(f"  - Failed: {stats['failed_tasks']}")
            print(f"  - Pending: {stats['pending_tasks']}")
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def _print_task_result(self, task):
        """Print task result."""
        if task.status.value == "completed":
            print(f"✅ Success: {task.processed_chunks} chunks ingested")
        else:
            print(f"❌ Failed: {task.error_message}")
    
    async def close(self):
        """Close connections."""
        await self.orchestrator.close()
        await self.embedding_service.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Document Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_parser.add_argument("path", help="File or directory path")
    ingest_parser.add_argument(
        "--pattern", default="*.*", help="File pattern (default: *.*)"
    )
    ingest_parser.add_argument(
        "--no-recursive", action="store_true", help="Don't search recursively"
    )
    ingest_parser.add_argument("--category", help="Document category")
    ingest_parser.add_argument(
        "--tags", nargs="+", help="Document tags"
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List documents")
    list_parser.add_argument(
        "--limit", type=int, default=50, help="Max results (default: 50)"
    )
    list_parser.add_argument(
        "--offset", type=int, default=0, help="Offset (default: 0)"
    )
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get document info")
    info_parser.add_argument("document_id", help="Document ID")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete document")
    delete_parser.add_argument("document_id", help="Document ID or --source")
    delete_parser.add_argument(
        "--source", action="store_true", help="Delete by source path"
    )
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search documents")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--top-k", type=int, default=5, help="Number of results (default: 5)"
    )
    search_parser.add_argument(
        "--threshold", type=float, default=0.7, help="Similarity threshold (default: 0.7)"
    )
    
    # Stats command
    subparsers.add_parser("stats", help="Show statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create CLI instance
    cli = RAGCLI()
    
    try:
        # Execute command
        if args.command == "ingest":
            asyncio.run(cli.ingest(
                args.path,
                recursive=not args.no_recursive,
                pattern=args.pattern,
                category=args.category,
                tags=args.tags,
            ))
        elif args.command == "list":
            cli.list_documents(limit=args.limit, offset=args.offset)
        elif args.command == "info":
            cli.get_info(args.document_id)
        elif args.command == "delete":
            if args.source:
                cli.delete_by_source(args.document_id)
            else:
                cli.delete(args.document_id)
        elif args.command == "search":
            asyncio.run(cli.search(
                args.query,
                top_k=args.top_k,
                threshold=args.threshold,
            ))
        elif args.command == "stats":
            cli.stats()
    finally:
        asyncio.run(cli.close())


if __name__ == "__main__":
    main()
