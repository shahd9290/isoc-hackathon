import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        await bot.load_extension("cogs.reminder")
        print("Reminder cog loaded!")
    except Exception as e:
        print(f"Error loading reminder cog: {e}")

# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)