from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
import time
from typing import List, Any
import shutil

class VectorStoreService:
    """
    Manages ChromaDB vector store for semantic search over video transcripts.
    
    Handles embedding generation, batch processing with rate limiting,
    and retrieval operations for the RAG pipeline.
    """
    
    def __init__(self):
        """Initialize embedding model with Google's latest text-embedding-004."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        # Use text-embedding-004 optimized for document retrieval tasks
        # task_type parameter improves embedding quality for semantic search
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            task_type="retrieval_document",
            google_api_key=api_key
        )
        self.vector_store = None

    def create_vector_store(self, chunks: List[str]):
        """
        Initialize ChromaDB and ingest transcript chunks with rate limit handling.
        
        Args:
            chunks: List of text chunks from video transcript
            
        Note:
            - Uses /tmp directory for Cloud Run compatibility (read-only root filesystem)
            - Implements exponential backoff for Google AI API rate limits
            - Batch size optimized for free tier (~15 requests/minute)
        """
        batch_size = 20  # Balanced for API limits and processing speed
        
        # Cloud Run instances have read-only root filesystem
        # /tmp is the only writable location for ephemeral storage
        persist_dir = "/tmp/chroma_db"
        
        # Remove stale database to prevent SQLite lock issues on instance restart
        if os.path.exists(persist_dir):
            try:
                shutil.rmtree(persist_dir)
            except Exception as e:
                print(f"Warning: Could not clear {persist_dir}: {e}")

        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            collection_name="video_transcript",
            persist_directory=persist_dir
        )
        
        total_chunks = len(chunks)
        print(f"Ingesting {total_chunks} chunks using text-embedding-004...")
        
        # Process in batches to respect API rate limits
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_chunks + batch_size - 1) // batch_size
            
            print(f"Processing batch {batch_num}/{total_batches}...")
            
            # Exponential backoff retry strategy for rate limit errors (429)
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    self.vector_store.add_texts(texts=batch)
                    break  # Success - proceed to next batch
                except Exception as e:
                    if "429" in str(e):
                        # Rate limit hit - wait with exponential backoff
                        wait_time = (2 ** attempt) * 2  # 2s, 4s, 8s, 16s, 32s
                        print(f"  Rate limit hit. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    else:
                        # Non-recoverable error - log and continue
                        print(f"  Critical Error on batch {batch_num}: {e}")
                        break
            
            # Brief pause between batches to avoid hitting rate limits
            time.sleep(1)

    def get_retriever(self) -> Any:
        """
        Returns LangChain retriever for semantic search.
        
        Returns:
            Retriever instance configured for similarity search
            
        Raises:
            ValueError: If vector store hasn't been initialized via create_vector_store()
        """
        if not self.vector_store:
            raise ValueError(
                "Vector store not initialized. "
                "Call create_vector_store() with transcript chunks first."
            )
        return self.vector_store.as_retriever()