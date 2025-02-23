import os

import discord
from dotenv import load_dotenv
from discord.ext import commands


from uhhhh import Zakat,Allahs99Names

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    #await bot.add_cog(Test(bot))  # Now we await it inside an async function
    await bot.add_cog(Zakat(bot))
    await bot.add_cog(Allahs99Names(bot))
    
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await load_cogs() 

bot.run(TOKEN)