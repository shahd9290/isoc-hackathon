import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)

# @client.event
@bot.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     if message.content.startswith('!hello'):
#         await message.channel.send('Hello!')

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


bot.run(TOKEN)