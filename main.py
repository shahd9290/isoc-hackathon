import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def addNum(ctx, *args):
    try:
        sum = 0
        for i in args:
            sum += int(i)
        await ctx.send(sum)
    except:
        await ctx.send("Detected Strings!")

bot.run(TOKEN)