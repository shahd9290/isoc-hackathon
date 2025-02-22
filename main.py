import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

from test import Test
from questions import Questions

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    await bot.add_cog(Test(bot))  # Now we await it inside an async function
    await bot.add_cog(Questions(bot))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Load both cogs
    await bot.load_extension("cogs.reminder")
    await bot.load_extension("cogs.dua")
    await bot.load_extension('cogs.hadith')
    print("All cogs loaded!")
async def load_cogs():
    await bot.add_cog(Test(bot))

bot.run(TOKEN)