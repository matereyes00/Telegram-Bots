import os
import logging
from knowledge_base_manager import setup_knowledge_base, get_conversation_chain
from games.sea_salt_and_paper import RULES_TEXT  # or however you load your rules
from telegram_handlers import setup_telegram_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Initializing knowledge base...")

    # Step 1: Set up the FAISS vectorstore using the game rules
    vectorstore = setup_knowledge_base(RULES_TEXT)
    logger.info("Knowledge base is ready.")

    # Step 2: Create the conversation chain using Gemini
    conversation_chain = get_conversation_chain(vectorstore)

    # Step 3: Start Telegram bot
    logger.info("Starting bot...")
    setup_telegram_bot(conversation_chain)


if __name__ == "__main__":
    main()
