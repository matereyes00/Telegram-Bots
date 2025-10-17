import os
import re
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
# New imports for handling conversation history
from langchain_core.messages import HumanMessage, AIMessage
from utils.game_logic import calculate_score, calculate_color_bonus
from knowledge_base_manager import get_conversation_chain

logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    """Escapes special characters for Telegram's MarkdownV2."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the user and tells them the bot is ready."""
    text = "Hello! I am the Game Master 🤖🎲\nAsk me anything about the rules of the current game or use the /score and /color_bonus commands!"
    escaped_text = escape_markdown(text)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=escaped_text,
        parse_mode=ParseMode.MARKDOWN_V2
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles questions from the user using a history-aware chain."""
    # Lazy initialization of the RAG chain
    if "rag_chain" not in context.application.bot_data:
        vectorstore = context.application.bot_data["vectorstore"]
        context.application.bot_data["rag_chain"] = get_conversation_chain(vectorstore)
        logger.info("RAG chain initialized on first use.")
    
    rag_chain = context.application.bot_data["rag_chain"]
    user_question = update.message.text
    
    # Use context.chat_data to store history for each unique user
    if 'history' not in context.chat_data:
        context.chat_data['history'] = []

    thinking_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🤔 Thinking..."
    )

    try:
        # Invoke the new chain with the user's input and their chat history
        response = await rag_chain.ainvoke({
            "input": user_question,
            "chat_history": context.chat_data.get('history', [])
        })

        answer = response.get("answer", "I'm not sure how to respond to that.")
        if not answer.strip():
            raise ValueError("Empty response from model")

        # Update the user's chat history with the new exchange
        context.chat_data['history'].extend([
            HumanMessage(content=user_question),
            AIMessage(content=answer)
        ])
        
        # Keep the history from getting too long
        if len(context.chat_data['history']) > 8:
            context.chat_data['history'] = context.chat_data['history'][-8:]

        final_text = escape_markdown(str(answer))
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_message.message_id,
            text=final_text,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    except Exception as e:
        logger.error(f"Error during conversation chain invocation: {e}")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=thinking_message.message_id,
            text="⚠️ Sorry, I had trouble generating an answer. Please try asking again."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logs errors."""
    logger.error(f"An error occurred: {context.error}")

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculates the score for a list of cards."""
    user_input = update.message.text.partition(' ')[2]
    if not user_input:
        example_text = "Please list your cards after the command\\. \nExample: `/score 2 crabs, 4 shells`"
        await update.message.reply_text(text=example_text, parse_mode=ParseMode.MARKDOWN_V2)
        return
    response_text, _ = calculate_score(user_input)
    escaped_response = escape_markdown(response_text)
    await update.message.reply_text(text=escaped_response, parse_mode=ParseMode.MARKDOWN_V2)

async def color_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculates the color bonus for a list of cards."""
    user_input = update.message.text.partition(' ')[2]
    if not user_input:
        example_text = "Please list your cards by color count\\. \nExample: `/color_bonus 4 blue, 3 pink, 1 mermaid`"
        await update.message.reply_text(text=example_text, parse_mode=ParseMode.MARKDOWN_V2)
        return
    response_text = calculate_color_bonus(user_input)
    escaped_response = escape_markdown(response_text)
    await update.message.reply_text(text=escaped_response, parse_mode=ParseMode.MARKDOWN_V2)

def setup_telegram_bot(vectorstore, port: int, webhook_url: str):
    """Initializes and runs the Telegram bot with webhooks."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

    app = Application.builder().token(bot_token).build()
    app.bot_data["vectorstore"] = vectorstore

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler('score', score))
    app.add_handler(CommandHandler('color_bonus', color_bonus))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info(f"Starting webhook server on 0.0.0.0:{port}")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=bot_token,
        webhook_url=f"{webhook_url}/{bot_token}"
    )

def setup_telegram_bot_local(vectorstore):
    """Initializes and runs the Telegram bot in polling mode for local development."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

    app = Application.builder().token(bot_token).build()
    app.bot_data["vectorstore"] = vectorstore

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler('score', score))
    app.add_handler(CommandHandler('color_bonus', color_bonus))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    logger.info("Bot is running in polling mode...")
    # This command fetches updates from Telegram directly.
    app.run_polling()
