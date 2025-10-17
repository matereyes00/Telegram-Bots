import logging
from knowledge_base_manager import load_knowledge_base
from telegram_handlers import setup_telegram_bot

# Configure logging for clear output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to initialize and run the bot.
    """
    # Step 1: Load the pre-built knowledge base from disk.
    # This is much faster than building it from scratch every time.
    try:
        vectorstore = load_knowledge_base()
        logger.info("Knowledge base is ready.")
    except FileNotFoundError as e:
        logger.error(e)
        logger.error("Exiting. Please make sure the vector store is created before running the bot.")
        return

    # Step 2: Start the bot and pass the loaded vectorstore.
    logger.info("Starting bot...")
    setup_telegram_bot(vectorstore)

if __name__ == "__main__":
    main()
