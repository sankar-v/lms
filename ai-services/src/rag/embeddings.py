from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import settings

class DocumentEmbedder:
    """Handles document loading, chunking, and embedding"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_documents(self, directory_path: str) -> List:
        """Load documents from a directory"""
        loader = DirectoryLoader(
            directory_path,
            glob="**/*.{md,txt,pdf}",
            loader_cls=TextLoader
        )
        documents = loader.load()
        return documents
    
    def chunk_documents(self, documents: List) -> List:
        """Split documents into chunks"""
        chunks = self.text_splitter.split_documents(documents)
        return chunks
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for a single text"""
        embedding = await self.embeddings.aembed_query(text)
        return embedding
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = await self.embeddings.aembed_documents(texts)
        return embeddings
