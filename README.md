# Sea Salt & Paper - Telegram Game Master Bot

This is a Python-based Telegram bot designed to be a game master for the card game "Sea Salt & Paper". It uses a powerful AI backend to answer rule-related questions and provides utility commands to help players with scoring.

The bot is optimized for fast, serverless deployment on platforms like Railway.

# About The Project

This bot has two primary functions:

- AI-Powered Rules Expert: Players can ask any question about the rules of "Sea Salt & Paper" in natural language. The bot uses a local vector database (FAISS) powered by LangChain and Google's Gemini model to provide accurate answers based on the game's official rulebook.
- Scoring Utilities: Players can use simple commands to calculate their scores for hands or color bonuses, removing the need for manual calculation.

```/score```: Calculates the point value of a player's hand.

```/color_bonus```: Calculates the color bonus based on mermaids and card colors.

The project is structured for high performance by pre-building the AI's knowledge base, which allows the bot to start up in seconds on a server.

# Getting Started

Follow these steps to get a local copy up and running for development and testing.

## Prerequisites

You will need the following software installed on your machine:

- Python 3.11 or higher. You can download it from the official Python website.

### Installation & Setup

1. Clone the repository:

```git clone <your-repository-url>```
```cd telegram-bot```

2. Create and activate a virtual environment. It is crucial to use Python 3.11 for this step.

# Create the virtual environment
```python3.11 -m venv .venv```

# Activate it (macOS/Linux)
```source .venv/bin/activate```

# Activate it (Windows)
```.\.venv\Scripts\activate```


### Install dependencies:

pip install -r requirements.txt


### Set up Environment Variables:
You'll need to provide secret keys for the bot to connect to Telegram and Google's AI services.

Create a file named .env in the root of your project.

Add the following lines to this file, replacing the placeholder text with your actual keys:

TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
GOOGLE_API_KEY="YOUR_GOOGLE_AI_STUDIO_API_KEY"
WEBHOOK_URL="YOUR_WEBHOOK_URL"


# Build the Knowledge Base (One-Time Step):
Before you can run the bot, you must build its knowledge base. This script downloads the AI model, processes the game rules, and saves the result to a local folder.

```python create_vectorstore.py```

This will create a faiss_index/ folder in your project. You must commit this folder to your Git repository.

## Usage

### Running the Bot Locally

After completing the setup, you can run the bot on your local machine for testing. The bot will start in webhook mode, but it won't be accessible to Telegram until deployed.

# Make sure your .env file is set up
python main.py


# Interacting with the Bot on Telegram

Once deployed, you can interact with the bot in your Telegram client.

```/start```: Displays a welcome message.

Ask a question: Simply type any question about the rules, e.g., "How many points are 3 penguins worth?" or "what happens if the deck runs out?".

```/score``` [cards]: Calculates the score of your cards.

Example: /score 2 crabs, 4 shells, 1 boat

```/color_bonus``` [colors]: Calculates the color bonus.

Example: ```/color_bonus``` 5 blue, 3 yellow, 2 mermaids

# Deployment to Railway

This bot is configured for easy deployment on Railway.

1. Push to GitHub: Make sure your project, including the faiss_index/ folder, is pushed to a GitHub repository.

2. Create a Railway Project:

2.a. Log in to Railway and create a new project, linking it to your GitHub repository.

2.b. Configure Environment Variables: In your Railway project dashboard, go to the Variables tab.

Add the TELEGRAM_BOT_TOKEN and GOOGLE_API_KEY with their respective values.

Railway automatically provides a PORT variable, which the application uses.

3. Generate a Public URL and Set Webhook:

Go to the Settings tab for your service.

Under Networking, click "+ Generate Domain". It will ask for a port; enter 8080.

Copy the generated public URL (ending in .up.railway.app).

4. Go back to the Variables tab and add a new variable:

Name: WEBHOOK_URL

Value: Paste the URL you just copied.

5. Railway will automatically deploy your application. The bot will be live and responding on Telegram.

# Project Structure

.
├── faiss_index/          # Pre-built AI knowledge base (Generated)
├── games/
│   └── sea_salt_and_paper.py # Contains the game rules text
├── .env                  # Local environment variables (Not committed)
├── .gitignore            # Files to ignore for Git
├── create_vectorstore.py # Script to build the knowledge base
├── game_logic.py         # Handles scoring calculations
├── knowledge_base_manager.py # Loads the knowledge base and handles AI queries
├── main.py               # Main application entry point
├── Procfile              # Command for Railway to run the bot
├── README.md             # This file
├── requirements.txt      # Python package dependencies
├── runtime.txt           # Specifies the Python version for deployment
└── telegram_handlers.py  # Defines bot commands and message handling
