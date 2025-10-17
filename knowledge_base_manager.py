import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

logger = logging.getLogger(__name__)

# --- THIS IS THE FUNCTION YOUR MAIN.PY NEEDS ---
def load_vectorstore():
    """Loads the pre-built FAISS index from the local directory."""
    logger.info("Loading vector store from 'faiss_index'...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Check if the index directory exists
    if not os.path.exists("faiss_index"):
        logger.error("The 'faiss_index' directory was not found. Please run create_vectorstore.py first.")
        raise FileNotFoundError("Could not find the FAISS index directory.")

    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    logger.info("Vector store loaded successfully.")
    return vectorstore


def get_conversation_chain(vectorstore):
    """Creates the conversational retrieval chain."""
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.6,
            max_output_tokens=1024,
            google_api_key=google_api_key,
        )
        logger.info("Using Gemini 1.5 Flash model.")
    except Exception as e:
        logger.warning(f"Falling back to Gemini Pro due to: {e}")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.6,
            max_output_tokens=1024,
            google_api_key=google_api_key,
        )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory
    )
    return chain

