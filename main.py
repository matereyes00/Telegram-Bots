import os
import logging
from knowledge_base_manager import setup_knowledge_base
from games.sea_salt_and_paper import RULES_TEXT
from telegram_handlers import setup_telegram_bot # <-- No get_conversation_chain needed here

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing knowledge base...")

    # Step 1: Set up the vectorstore
    vectorstore = setup_knowledge_base(RULES_TEXT)
    logger.info("Knowledge base is ready.")

    # Step 2: Start the bot, passing only the vectorstore
    logger.info("Starting bot...")
    setup_telegram_bot(vectorstore) # <-- Pass the vectorstore here

if __name__ == "__main__":
    main()