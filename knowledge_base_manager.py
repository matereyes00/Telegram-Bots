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
FAISS_INDEX_PATH = "faiss_index"

def load_knowledge_base():
    """
    Loads the pre-built FAISS vector store from the local disk.
    """
    logger.info("Loading knowledge base from disk...")
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(
            f"FAISS index not found at '{FAISS_INDEX_PATH}'. "
            "Please run 'create_vectorstore.py' first to generate it."
        )
    
    # Initialize the same embeddings model used to create the store
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load the vector store, allowing pickled files
    vectorstore = FAISS.load_local(
        FAISS_INDEX_PATH, 
        embeddings,
        # This is required for loading FAISS indexes with newer LangChain versions
        allow_dangerous_deserialization=True 
    )
    logger.info("Knowledge base loaded successfully.")
    return vectorstore


def get_conversation_chain(vectorstore):
    """
    Creates a conversational retrieval chain using the loaded vector store.
    """
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            max_output_tokens=1024,
            google_api_key=google_api_key,
        )
        logger.info("Using Gemini 1.5 Flash model.")
    except Exception as e:
        logger.warning(f"Could not initialize Flash model, falling back to Pro. Error: {e}")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
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
