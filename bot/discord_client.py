import os
import discord
import aiohttp
import asyncio
import json
import logging
import tempfile
from discord.ext import commands
from dotenv import load_dotenv

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

# Server URLs
SERVER_BASE_URL = os.getenv('SERVER_BASE_URL', 'http://localhost:8000')
CHAT_ENDPOINT = f"{SERVER_BASE_URL}/chat"
EMOTION_CHAT_ENDPOINT = f"{SERVER_BASE_URL}/emotion_chat"
ADD_URL_ENDPOINT = f"{SERVER_BASE_URL}/add_urls"
ADD_TEXT_ENDPOINT = f"{SERVER_BASE_URL}/add_texts"
ADD_PDF_ENDPOINT = f"{SERVER_BASE_URL}/add_pdfs"

# Intents configuration
intents = discord.Intents.default()
intents.message_content = True  # Needed to read message content
intents.messages = True

# Initialize bot with command prefix
bot = commands.Bot(command_prefix='!', intents=intents)


async def send_request(url, params):
    """Send requests to the AI server and handle responses"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Error {response.status}: {error_text}")
                    return {"message": f"Error: Server returned status {response.status}"}
        except aiohttp.ClientError as e:
            logger.error(f"Request error: {str(e)}")
            return {"message": f"Connection error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"message": f"Unexpected error: {str(e)}"}


async def upload_file(url, file_path, filename=None):
    """Upload a file to the server"""
    if not filename:
        filename = os.path.basename(file_path)

    async with aiohttp.ClientSession() as session:
        try:
            with open(file_path, 'rb') as f:
                form_data = aiohttp.FormData()
                form_data.add_field('file', f, filename=filename)

                async with session.post(url, data=form_data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"Error {response.status}: {error_text}")
                        return {"message": f"Error: Server returned status {response.status}"}
        except aiohttp.ClientError as e:
            logger.error(f"Request error: {str(e)}")
            return {"message": f"Connection error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"message": f"Unexpected error: {str(e)}"}


@bot.event
async def on_ready():
    """Event triggered when the bot is ready"""
    logger.info(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="your queries | !help for commands"
    ))


@bot.command(name='help', help='Shows the available commands')
async def help_command(ctx):
    """Display help information"""
    embed = discord.Embed(
        title="AI Assistant Bot Commands",
        description="Here are the commands you can use:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="!chat [message]",
        value="Chat with the AI assistant",
        inline=False
    )

    embed.add_field(
        name="!emotion [message]",
        value="Chat with emotion-aware responses",
        inline=False
    )

    embed.add_field(
        name="!learn_url [url]",
        value="Add a URL to the knowledge base",
        inline=False
    )

    embed.add_field(
        name="!learn_text [text]",
        value="Add text to the knowledge base",
        inline=False
    )

    embed.add_field(
        name="!learn_pdf",
        value="Add a PDF to the knowledge base (attach a PDF file with this command)",
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command(name='chat', help='Chat with the AI assistant')
async def chat_command(ctx, *, message=None):
    """Forward messages to the chat endpoint"""
    if not message:
        await ctx.send("Please provide a message to chat with the assistant.")
        return

    async with ctx.typing():  # Show typing indicator while waiting for response
        response = await send_request(CHAT_ENDPOINT, {"query": message})

        if response and "message" in response:
            # Split long messages if needed (Discord has a 2000 character limit)
            message_content = response["message"]
            for i in range(0, len(message_content), 1900):
                chunk = message_content[i:i+1900]
                await ctx.send(chunk)
        else:
            await ctx.send("Sorry, I couldn't get a response from the server.")


@bot.command(name='emotion', help='Chat with emotion-aware responses')
async def emotion_chat_command(ctx, *, message=None):
    """Forward messages to the emotion chat endpoint"""
    if not message:
        await ctx.send("Please provide a message for the emotion-aware chat.")
        return

    async with ctx.typing():
        response = await send_request(EMOTION_CHAT_ENDPOINT, {"query": message})

        if response and "message" in response:
            message_content = response["message"]

            # Create an embed with the emotion analysis if available
            if "emotion_analysis" in response:
                emotion = response.get("emotion_analysis", {})
                embed = discord.Embed(
                    title="Emotion Analysis",
                    color=discord.Color.purple()
                )

                if emotion.get("primary_emotion"):
                    embed.add_field(
                        name="Primary Emotion",
                        value=emotion.get("primary_emotion", "Unknown"),
                        inline=True
                    )

                if emotion.get("sentiment"):
                    embed.add_field(
                        name="Sentiment",
                        value=emotion.get("sentiment", "Unknown"),
                        inline=True
                    )

                if emotion.get("intensity"):
                    embed.add_field(
                        name="Intensity",
                        value=f"{emotion.get('intensity', 3)}/5",
                        inline=True
                    )

                # Send the message content first
                for i in range(0, len(message_content), 1900):
                    chunk = message_content[i:i+1900]
                    await ctx.send(chunk)

                # Then send the emotion analysis
                await ctx.send(embed=embed)
            else:
                # Just send the message if no emotion analysis is available
                for i in range(0, len(message_content), 1900):
                    chunk = message_content[i:i+1900]
                    await ctx.send(chunk)
        else:
            await ctx.send("Sorry, I couldn't get a response from the server.")


@bot.command(name='learn_url', help='Add a URL to the knowledge base')
async def learn_url_command(ctx, url=None):
    """Add a URL to the knowledge base"""
    if not url:
        await ctx.send("Please provide a URL to learn from.")
        return

    async with ctx.typing():
        await ctx.send(f"Learning from URL: {url}")
        response = await send_request(ADD_URL_ENDPOINT, {"url": url})

        if response and "message" in response:
            await ctx.send(response["message"])
        else:
            await ctx.send("Sorry, I couldn't get a response from the server.")


@bot.command(name='learn_text', help='Add text to the knowledge base')
async def learn_text_command(ctx, *, text=None):
    """Add text to the knowledge base"""
    if not text:
        await ctx.send("Please provide text to learn from.")
        return

    async with ctx.typing():
        await ctx.send("Processing your text...")
        response = await send_request(ADD_TEXT_ENDPOINT, {"text": text})

        if response and "message" in response:
            await ctx.send(response["message"])
        else:
            await ctx.send("Sorry, I couldn't get a response from the server.")


@bot.command(name='learn_pdf', help='Add a PDF to the knowledge base')
async def learn_pdf_command(ctx):
    """Add a PDF to the knowledge base"""
    if not ctx.message.attachments:
        await ctx.send("Please attach a PDF file to learn from.")
        return

    attachment = ctx.message.attachments[0]

    # Check if the attachment is a PDF
    if not attachment.filename.lower().endswith('.pdf'):
        await ctx.send("The attached file is not a PDF. Please upload a PDF file.")
        return

    async with ctx.typing():
        await ctx.send(f"Processing PDF: {attachment.filename}")

        # Create a temporary file to save the attachment
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_filename = temp_file.name

        # Download the attachment
        try:
            await attachment.save(temp_filename)

            # Upload the file to the server
            response = await upload_file(ADD_PDF_ENDPOINT, temp_filename, attachment.filename)

            if response and "message" in response:
                await ctx.send(response["message"])
            else:
                await ctx.send("Sorry, I couldn't get a response from the server.")
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            await ctx.send(f"Error processing the PDF: {str(e)}")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Type `!help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param.name}")
    else:
        await ctx.send(f"An error occurred: {str(error)}")
        logger.error(f"Command error: {str(error)}")

# Direct message handling (optional feature)


@bot.event
async def on_message(message):
    """Process messages and handle DMs"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Process commands first (this is important!)
    await bot.process_commands(message)

    # If it's a DM and not a command, treat it as a chat message
    if isinstance(message.channel, discord.DMChannel) and not message.content.startswith(bot.command_prefix):
        async with message.channel.typing():
            response = await send_request(CHAT_ENDPOINT, {"query": message.content})

            if response and "message" in response:
                # Split long messages if needed
                message_content = response["message"]
                for i in range(0, len(message_content), 1900):
                    chunk = message_content[i:i+1900]
                    await message.channel.send(chunk)
            else:
                await message.channel.send("Sorry, I couldn't get a response from the server.")


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
