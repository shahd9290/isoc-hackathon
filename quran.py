from discord.ext import commands
import discord
import json

# Inspiration: https://github.com/risan/quran-json?tab=readme-ov-file

class Quran(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open("data/quran.json", encoding='utf-8') as quran:
            self.quran = json.load(quran)

        with open("data/en.json", encoding='utf-8') as en:
            self.quran_en = json.load(en)

        with open("data/transliteration.json", encoding='utf-8') as transliteration:
            self.transliteration = json.load(transliteration)

        with open("data/chapters.json", encoding='utf-8') as chapters:
            self.chapters = json.load(chapters)

    @commands.command()
    async def randomVerse(self, ctx):
        pass

    @commands.command()
    async def translateVerse(self,ctx):
        pass

    @commands.command()
    async def listenToVerse(self, ctx):
        pass

    @commands.command()
    async def surah(self, ctx, surah_num):
        name = self.chapters[int(surah_num)-1]["name"]
        name_trans = self.chapters[int(surah_num)-1]["transliteration"]
        msg = f"# __{name} - {name_trans}__ \n"
        for verse in self.quran[surah_num]:
            msg += f"## ﴾{verse["verse"]}﴿ - {verse["text"]}\n"
        await ctx.send(msg)