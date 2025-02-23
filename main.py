import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Load both cogs
    await bot.load_extension("cogs.reminder")
    await bot.load_extension("cogs.dua")
    print("All cogs loaded!")

bot.run(TOKEN)