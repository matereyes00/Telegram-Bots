import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()  
google_api_key = os.getenv("GOOGLE_API_KEY")

logger = logging.getLogger(__name__)

def setup_knowledge_base(game_rules_text: str):
    logger.info("Setting up knowledge base for the selected game...")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(game_rules_text)
    docs = [Document(page_content=chunk) for chunk in chunks]

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    try:
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",
            temperature=0.6,
            max_output_tokens=1024,
            google_api_key=google_api_key,  # ✅ added
        )
        logger.info("Using Gemini 2.5 Flash model.")
    except Exception as e:
        logger.warning(f"Falling back to Gemini Pro due to: {e}")
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-pro-latest",
            temperature=0.6,
            max_output_tokens=1024,
            google_api_key=google_api_key,  # ✅ added
        )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory
    )
    return chain
