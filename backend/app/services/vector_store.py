from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
import time
from typing import List, Any
import shutil

class VectorStoreService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        # FIX 1: Use the newer model. 'embedding-001' is deprecated (Limit: 0).
        # We also specify 'task_type' which improves quality for retrieval.
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            task_type="retrieval_document",
            google_api_key=api_key
        )
        self.vector_store = None

    def create_vector_store(self, chunks: List[str]):
        """
        Creates a new in-memory vector store with robust rate limit handling.
        """
        # FIX 2: Optimized Batching for Free Tier
        # Free tier allows ~15 requests per minute. 
        # A batch size of 10-20 is efficient, but we need robust sleeping.
        batch_size = 20 
        
        # Initialize empty vector store
        # FIX: Use /tmp for persistence in Cloud Functions (read-only root fs)
        persist_dir = "/tmp/chroma_db"
        
        # Clean up existing /tmp/chroma_db if it exists to avoid lock issues on restart
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
        
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_chunks + batch_size - 1) // batch_size
            
            print(f"Processing batch {batch_num}/{total_batches}...")
            
            # FIX 3: Robust Exponential Backoff Retry Loop
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    self.vector_store.add_texts(texts=batch)
                    break # Success! Exit the retry loop
                except Exception as e:
                    if "429" in str(e):
                        wait_time = (2 ** attempt) * 2  # Exponential: 2s, 4s, 8s, 16s...
                        print(f"  Rate limit hit. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    else:
                        print(f"  Critical Error on batch {batch_num}: {e}")
                        break # Stop if it's not a rate limit error
            
            # Standard "courtesy sleep" between successful batches
            time.sleep(1) 

    def get_retriever(self) -> Any:
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Please ingest documents first.")
        return self.vector_store.as_retriever()