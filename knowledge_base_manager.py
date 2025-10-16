import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# --- Step 1: Load Google API key from environment ---
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


# --- Step 2: Set up the FAISS knowledge base ---
def setup_knowledge_base(game_rules_text: str):
    logger.info("Setting up knowledge base for the selected game...")

    # Split the input text into overlapping chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(game_rules_text)
    docs = [Document(page_content=chunk) for chunk in chunks]

    # Use HuggingFace embeddings for semantic search
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create the FAISS index
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore


# --- Step 3: Create the conversation chain ---
def get_conversation_chain(vectorstore):
    try:
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",
            temperature=0.6,
            max_output_tokens=1024,
        )
        logger.info("Using Gemini 2.5 Flash model.")
    except Exception as e:
        # Fallback to Gemini Pro if needed
        logger.warning(f"Falling back to Gemini Pro due to: {e}")
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-pro-latest",
            temperature=0.6,
            max_output_tokens=1024,
        )

    # Use conversational memory to preserve chat context
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # Combine LLM + retriever + memory into one chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory
    )

    return chain
