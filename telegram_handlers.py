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
from game_logic import calculate_score, calculate_color_bonus
from knowledge_base_manager import get_conversation_chain

logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    """Escapes special characters for Telegram's MarkdownV2."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the user and tells them the bot is ready."""
    text = "Hello! I am the Game Master 🤖🎲\nAsk me anything about the rules of the current game!"
    escaped_text = escape_markdown(text)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=escaped_text,
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles questions from the user."""
    if "conversation_chain" not in context.application.bot_data:
        vectorstore = context.application.bot_data["vectorstore"]
        context.application.bot_data["conversation_chain"] = get_conversation_chain(vectorstore)
        logger.info("Conversation chain initialized on first use.")
    
    conversation_chain = context.application.bot_data["conversation_chain"]
    user_question = update.message.text
    
    thinking_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🤔 Thinking..."
    )

    try:
        response = await conversation_chain.ainvoke({"question": user_question})
        answer = response.get("answer", "Sorry, I couldn't find an answer.")
        if not answer or not str(answer).strip():
            raise ValueError("Empty response from model")
        
        final_text = escape_markdown(str(answer))

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_message.message_id,
            text=final_text,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    except Exception as e:
        logger.error(f"Error during conversation chain invocation: {e}")
        error_text = escape_markdown("⚠️ Sorry, I couldn’t generate a proper answer. Please try rephrasing your question.")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_message.message_id,
            text=error_text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logs errors."""
    logger.error(f"An error occurred: {context.error}")


async def color_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculates the color bonus for a list of cards."""
    user_input = update.message.text.partition(' ')[2]

    if not user_input:
        example_text = "Please list your cards by color count\\. \nExample: `/color\\-bonus 4 blue, 3 pink, 1 mermaid`"
        await update.message.reply_text(text=example_text, parse_mode=ParseMode.MARKDOWN_V2)
        return

    response_text = calculate_color_bonus(user_input)
    escaped_response = escape_markdown(response_text)
    await update.message.reply_text(
        text=escaped_response,
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculates the score for a list of cards provided by the user."""
    user_input = update.message.text.partition(' ')[2]

    if not user_input:
        error_text = "Please list your cards after the command\\. \nExample: `/score 2 crabs, 4 shells`"
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


# --- KEY CHANGE 1: Function now accepts port and webhook_url ---
def setup_telegram_bot(vectorstore, port: int, webhook_url: str):
    """Initializes and runs the Telegram bot with webhooks."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

    app = ApplicationBuilder().token(bot_token).build()

    app.bot_data["vectorstore"] = vectorstore

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler('score', score))
    app.add_handler(CommandHandler('color_bonus', color_bonus))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    # --- KEY CHANGE 2: This command runs the bot in webhook mode ---
    logger.info(f"Starting webhook server on 0.0.0.0:{port}")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=webhook_url
    )

