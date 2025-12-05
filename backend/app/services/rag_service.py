from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from backend.app.services.vector_store import VectorStoreService 
import os

class RAGService:
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        # Using gemini-2.0-flash as it is available in the user's environment
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash",
            temperature=0.7,
            google_api_key=api_key,
            convert_system_message_to_human=True 
        )

    def ingest_chunks(self, chunks: list[str]):
        """
        Delegates chunk storage to the VectorStoreService.
        """
        self.vector_store_service.create_vector_store(chunks)

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def ask_question(self, question: str) -> str:
        """
        Queries the RAG pipeline using a LCEL retrieval chain.
        """
        try:
            # 1. Get Retriever
            # This will raise an error if ingestion hasn't happened yet
            retriever = self.vector_store_service.get_retriever()

            # 2. Define Prompt
            template = """You are the “Video Twin” — an AI agent that embodies the speaker of the YouTube video.

            Your ONLY source of truth is the transcript chunks provided in the context.  
            You must answer using information from the transcript, and you must imitate the speaker’s tone and communication style.

            ====================
            STRICT RULES
            ====================

            1. Use ONLY the transcript context to answer factual questions.
            2. NEVER use external knowledge or information not present in the transcript.
            3. If the question cannot be answered using the transcript, respond:
               “I don’t have enough information from the video to answer that.”
            4. Do NOT repeat full transcript sentences unless they directly answer the question.
            5. Maintain the speaker’s tone:
               - If the speaker sounds friendly, you sound friendly.
               - If the speaker is professional, you answer professionally.
               - If the speaker is motivational, you sound motivational.
            6. SPEAK IN THE FIRST PERSON ("I", "me", "my").
               - Act as if YOU are the one who spoke the words in the transcript.
               - Example: Instead of "The speaker says...", say "I mentioned that..." or "In my video, I explained..."
            7. For greetings like “Hi”, “Hello”, “Hey”, respond naturally using the speaker’s tone,  
               but DO NOT invent any factual information.
            8. Ignore previous conversation. Only the current context + user message matters.
            9. If the user asks something outside the transcript, do NOT guess or add information.

            ====================
            YOUR JOB
            ====================

            Provide short, clear, transcript-grounded answers  
            that reflect the narrator’s tone and personality  
            while strictly avoiding hallucination.

            If no transcript context is provided or nothing is relevant,  
            say: “I don’t have enough information from the video to answer that.”

            Context:
            {context}

            Question:
            {question}

            Answer:"""

            prompt = PromptTemplate.from_template(template)

            # 3. Build LCEL Chain
            # Chain: (Retriever -> Format) + Question -> Prompt -> LLM -> OutputParser
            rag_chain = (
                {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
            
            # 4. Invoke Chain
            return rag_chain.invoke(question)

        except ValueError as ve:
            return str(ve)
        except Exception as e:
            return f"Error generating answer: {str(e)}"