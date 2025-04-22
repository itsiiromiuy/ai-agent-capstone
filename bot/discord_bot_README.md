# Discord Bot for AI Agent Integration

This Discord bot serves as a client for your AI agent server, allowing users to interact with your multi-agent system directly through Discord.

## Features

- Chat with the AI assistant using the `!chat` command
- Get emotion-aware responses with the `!emotion` command
- Add URLs to the knowledge base with `!learn_url`
- Add text to the knowledge base with `!learn_text`
- Upload PDF files to the knowledge base with `!learn_pdf`
- Direct message support - chat directly with the bot without using commands

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip or pipenv
- Discord account with bot creation privileges
- Your AI agent server running

### Step 1: Create a Discord Bot
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click on "New Application" and give your bot a name
3. Navigate to the "Bot" tab and click "Add Bot"
4. Under the "Privileged Gateway Intents" section, enable:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent (important for reading messages)
5. Copy your bot token (you'll need this later)

### Step 2: Invite the Bot to Your Server

1. In the Discord Developer Portal, go to the "OAuth2" tab
2. Under "OAuth2 URL Generator", select the "bot" scope
3. Select the following bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History
   - Use Slash Commands
4. Copy the generated URL and open it in your browser
5. Select the server where you want to add the bot and authorize it

### Step 3: Configure Environment Variables

Create a `.env` file in the bot directory with the following variables:

```
DISCORD_TOKEN=your_discord_bot_token
SERVER_BASE_URL=http://localhost:8000  # Update with your server URL if different
```

### Step 4: Install Dependencies

```bash
pip install discord.py aiohttp python-dotenv
```

Or if using pipenv:

```bash
pipenv install discord.py aiohttp python-dotenv
```

### Step 5: Run the Bot

Navigate to the bot directory first

```bash
cd bot

# Then run the Discord client
pipenv run python discord_client.py
```

## Usage

Once the bot is running and added to your server, you can use the following commands:

- `!commands` - Shows all available commands
- `!chat [message]` - Chat with the AI assistant
  - Example: `!chat What's the weather like today?`
- `!emotion [message]` - Get emotion-aware responses
  - Example: `!emotion I'm feeling really excited about this project!`
- `!learn_url [url]` - Add a URL to the knowledge base
  - Example: `!learn_url https://en.wikipedia.org/wiki/Artificial_intelligence`
- `!learn_text [text]` - Add text to the knowledge base
  - Example: `!learn_text Artificial intelligence is intelligence demonstrated by machines.`
- `!learn_pdf` - Add a PDF to the knowledge base
  - To use this command, attach a PDF file to your message when sending the command
  - Example: Type `!learn_pdf` and attach a document.pdf file to the message

You can also send direct messages to the bot to chat without using the `!chat` prefix.

## File Upload Guide

The bot supports uploading PDF files to enhance your AI's knowledge base:

1. Type the `!learn_pdf` command in a Discord channel
2. Click the plus icon (+) next to the message input
3. Select "Upload a File" and choose your PDF
4. Send the message with the command and attached file
5. The bot will process the PDF and add it to the knowledge base
6. You'll receive a confirmation message when processing is complete

## Troubleshooting

### Bot Not Responding

1. Ensure your AI agent server is running
2. Check that the SERVER_BASE_URL in your .env file is correct
3. Make sure the bot has the necessary permissions in the Discord server
4. Check the console logs for any error messages

### Connection Errors

If you see connection errors, ensure that:
1. Your AI agent server is accessible at the URL specified in SERVER_BASE_URL
2. The required endpoints (/chat, /emotion_chat, etc.) are available on your server
3. Your network allows the connection between the Discord bot and your server

### File Upload Issues

If you're having problems with PDF uploads:
1. Make sure the file is a valid PDF (check the file extension)
2. Verify the file isn't too large (Discord has an 8MB limit for regular users)
3. Ensure the server's `/add_pdfs` endpoint is working correctly
4. Check the bot's console logs for detailed error messages

## Extending the Bot

You can extend the bot's functionality by:

1. Adding new commands in discord_client.py
2. Connecting to additional endpoints on your server
3. Adding support for other file types or Discord features

## Technical Details

The bot uses:
- discord.py library for Discord API integration
- aiohttp for asynchronous HTTP requests to your server
- tempfile for temporary storage of uploaded files
- FormData for multipart/form-data file uploads to the server 

# Initialize bot with command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Disable the default help command
bot.remove_command('help')

# Now you can define your own help command
@bot.command(name='help', help='Shows the available commands')
async def help_command(ctx):
    # Your help command code here 