import os
import logging
from knowledge_base_manager import load_vectorstore
from telegram_handlers import setup_telegram_bot_local # <-- We will create this new function

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main_local():
    """Initializes and runs the bot in polling mode for local development."""
    logger.info("Starting bot in LOCAL POLLING mode...")
    
    logger.info("Loading knowledge base from disk...")
    vectorstore = load_vectorstore()
    logger.info("Knowledge base is ready.")

    # Call the new local setup function in telegram_handlers
    setup_telegram_bot_local(vectorstore)

if __name__ == "__main__":
    main_local()
