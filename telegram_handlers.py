import os
import re
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from game_logic import calculate_score # <-- Import the new function

logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    """Escapes special characters for Telegram's MarkdownV2."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


# --- Command handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the user and tells them the bot is ready."""
    # Define the text for the welcome message
    text = "Hello! I am the Game Master 🤖🎲\nAsk me anything about the rules of the current game!"
    
    # Escape the text before sending it
    escaped_text = escape_markdown(text)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=escaped_text,  # <-- Use the escaped text variable here
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles questions from the user."""
    user_question = update.message.text

    if "conversation_chain" not in context.application.bot_data:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, my knowledge base isn't loaded correctly. Please try restarting me."
        )
        return

    conversation_chain = context.application.bot_data["conversation_chain"]
    thinking_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🤔 Thinking..."
    )

    try:
        response = await conversation_chain.ainvoke({"question": user_question})

        # Try multiple fallback fields
        answer = (
            getattr(response, "content", None)
            or response.get("answer")
            or (
                response.get("chat_history")[-1].content
                if response.get("chat_history")
                else None
            )
        )

        if not answer or not str(answer).strip():
            raise ValueError("Empty response from model")
        
        escaped_answer = escape_markdown(answer) 

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_message.message_id,
            text=escaped_answer,
            parse_mode=ParseMode.MARKDOWN_V2 # <-- Add this line
        )

    except Exception as e:
        logger.error(f"Error during conversation chain invocation: {e}")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_message.message_id,
            text="⚠️ Sorry, I couldn’t generate a proper answer. Please try rephrasing your question."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logs errors."""
    logger.error(f"An error occurred: {context.error}")


# --- Bot setup function ---

def setup_telegram_bot(conversation_chain):
    """Initializes and runs the Telegram bot."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

    app = ApplicationBuilder().token(bot_token).build()

    # Store the conversation chain in bot_data
    app.bot_data["conversation_chain"] = conversation_chain

    # Register command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler('score', score)) # <-- Add this line
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Bot is running...")
    app.run_polling()


async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculates the score for a list of cards provided by the user."""
    user_input = update.message.text.partition(' ')[2] # Get text after /score

    if not user_input:
        error_text = "Please list your cards after the command\. \nExample: `/score 2 crabs, 4 shells`"
        
        # You don't need to escape this specific string since I've already
        # manually escaped the period for you with a '\'.
        # For any other text, always use the escape_markdown() function.
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=error_text,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    response_text, _ = calculate_score(user_input)
    escaped_response = escape_markdown(response_text) 

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=escaped_response,
        parse_mode=ParseMode.MARKDOWN_V2
    )