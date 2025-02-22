from discord.ext import commands
import discord
import json

# Inspiration: https://github.com/risan/quran-json?tab=readme-ov-file

class Quran(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def randomVerse(self, ctx):
        pass

    @commands.command()
    async def translateVerse(self,ctx):
        pass

    @commands.command()
    async def listenToVerse(self, ctx):
        pass