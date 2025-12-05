from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from backend.app.services.vector_store import VectorStoreService 
import os

class RAGService:
    """
    Orchestrates Retrieval-Augmented Generation pipeline for video Q&A.
    
    Combines semantic search over transcript chunks with LLM generation
    to provide accurate, context-grounded answers that mimic the video speaker's tone.
    """
    
    def __init__(self):
        """Initialize vector store and LLM with production-ready configuration."""
        self.vector_store_service = VectorStoreService()
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        # Gemini 2.0 Flash: Fast, cost-effective model optimized for conversational AI
        # Temperature 0.7 balances creativity with factual accuracy
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash",
            temperature=0.7,
            google_api_key=api_key,
            convert_system_message_to_human=True  # Required for Gemini API compatibility
        )

    def ingest_chunks(self, chunks: list[str]):
        """
        Store transcript chunks in vector database for semantic retrieval.
        
        Args:
            chunks: List of text segments from video transcript
            
        Note:
            This must be called before ask_question() to populate the knowledge base.
        """
        self.vector_store_service.create_vector_store(chunks)

    def _format_docs(self, docs):
        """
        Concatenate retrieved documents into single context string.
        
        Args:
            docs: List of LangChain Document objects from retriever
            
        Returns:
            Formatted context string with double newlines between chunks
        """
        return "\n\n".join(doc.page_content for doc in docs)

    def ask_question(self, question: str) -> str:
        """
        Execute RAG pipeline: retrieve relevant context + generate grounded answer.
        
        Pipeline stages:
            1. Semantic search: Find most relevant transcript chunks
            2. Context formatting: Prepare retrieved text for LLM
            3. Prompt construction: Inject context + question into template
            4. LLM generation: Generate answer following strict grounding rules
            5. Output parsing: Extract clean text response
            
        Args:
            question: User's question about the video
            
        Returns:
            AI-generated answer grounded in transcript context
            
        Raises:
            ValueError: If vector store not initialized (no video ingested)
            Exception: If LLM generation fails
            
        Note:
            System prompt enforces strict context adherence to prevent hallucination.
            Answers are designed to mimic the video speaker's tone and perspective.
        """
        try:
            # Retrieve semantically similar chunks from vector store
            retriever = self.vector_store_service.get_retriever()

            # System prompt engineering for "Video Twin" persona
            # Key constraints: context-only answers, speaker's tone, first-person perspective
            template = """You are the "Video Twin" — an AI agent that embodies the speaker of the YouTube video.

            Your ONLY source of truth is the transcript chunks provided in the context.  
            You must answer using information from the transcript, and you must imitate the speaker's tone and communication style.

            ====================
            STRICT RULES
            ====================

            1. Use ONLY the transcript context to answer factual questions.
            2. NEVER use external knowledge or information not present in the transcript.
            3. If the question cannot be answered using the transcript, respond:
               "I don't have enough information from the video to answer that."
            4. Do NOT repeat full transcript sentences unless they directly answer the question.
            5. Maintain the speaker's tone:
               - If the speaker sounds friendly, you sound friendly.
               - If the speaker is professional, you answer professionally.
               - If the speaker is motivational, you sound motivational.
            6. SPEAK IN THE FIRST PERSON ("I", "me", "my").
               - Act as if YOU are the one who spoke the words in the transcript.
               - Example: Instead of "The speaker says...", say "I mentioned that..." or "In my video, I explained..."
            7. For greetings like "Hi", "Hello", "Hey", respond naturally using the speaker's tone,  
               but DO NOT invent any factual information.
            8. Ignore previous conversation. Only the current context + user message matters.
            9. If the user asks something outside the transcript, do NOT guess or add information.

            ====================
            YOUR JOB
            ====================

            Provide short, clear, transcript-grounded answers  
            that reflect the narrator's tone and personality  
            while strictly avoiding hallucination.

            If no transcript context is provided or nothing is relevant,  
            say: "I don't have enough information from the video to answer that."

            Context:
            {context}

            Question:
            {question}

            Answer:"""

            prompt = PromptTemplate.from_template(template)

            # LangChain Expression Language (LCEL) chain composition
            # Parallel execution: retriever + question passthrough → prompt → LLM → parser
            rag_chain = (
                {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
            
            # Execute chain and return generated answer
            return rag_chain.invoke(question)

        except ValueError as ve:
            # Vector store not initialized - user needs to ingest video first
            return str(ve)
        except Exception as e:
            # Catch-all for LLM API errors, network issues, etc.
            return f"Error generating answer: {str(e)}"