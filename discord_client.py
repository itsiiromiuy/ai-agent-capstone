import os
import discord
import asyncio
import json
import logging
import tempfile
from discord.ext import commands
from dotenv import load_dotenv
from bot.server import ai_agent
from textwrap import wrap

MAX_DISCORD_MESSAGE_LENGTH = 2000

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord_client')

# Discord bot token from environment variable
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable not set")


# Intents configuration
intents = discord.Intents.default()
intents.message_content = True  # Needed to read message content
intents.messages = True

# Initialize bot with command prefix
bot = commands.Bot(command_prefix='!', intents=intents)


async def send_long_messages(context, message):
    sections = wrap(message, MAX_DISCORD_MESSAGE_LENGTH)
    for section in sections:
        await context.send(section)


@bot.event
async def on_ready():
    """Event triggered when the bot is ready"""
    logger.info(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="your queries | !help for commands"
    ))


@bot.command(name='chat', help='Chat with the AI assistant')
async def chat_command(ctx, *, message=None):
    """Forward messages to the chat endpoint"""
    if not message:
        await ctx.send("Please provide a message to chat with the assistant.")
        return

    response = ai_agent.run(message)
    last_message = response["messages"][-1]
    await send_long_messages(ctx, last_message["content"])


def main():
    """Main function to start the bot"""
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        logger.error("Failed to login. Check your Discord token.")
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}")


if __name__ == "__main__":
    main()
