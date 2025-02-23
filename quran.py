from discord.ext import commands
import json
import random

# Data Source: https://github.com/risan/quran-json?tab=readme-ov-file

class Quran(commands.Cog):
    """
    This component is used to allow the user to interact with various features of the Quran, including reading individual verses or an entire surah.
    """
    def __init__(self, bot):
        """
        Initialises the Quran component and pre-loads data from the JSON files.
        :param bot: The bot object used to send commands.
        """
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
    async def randomverse(self, ctx) -> None:
        """
        Generates a random verse of the Quran with translation and meaning.
        :param ctx: The context of the channel this was called from
        :return: None
        """
        surah = self.chapters[random.randint(0, 113)]
        verse_num = random.randint(0, surah["total_verses"]-1)
        await self.response(ctx, surah, verse_num)

    @commands.command()
    async def verse(self,ctx, *args):
        """
        Generates a verse of the Quran based on the user's input, along with translation and meaning.
        :param ctx: The context of the channel this was called from
        :param args: The surah and verse that the user wishes to process (e.g 114:1)
        :return: None
        """
        try:
            if len(args) == 0:
                raise Exception()
            surahVerse = args[0]
            surah_num, verse_num = surahVerse.split(":")
            if int(surah_num) <= 0 or int(verse_num) <= 0:
                raise Exception()
            surah = self.chapters[int(surah_num)-1]
            verse_num = int(verse_num)
            await self.response(ctx, surah, verse_num-1)
        except:
            await ctx.send("Please enter a valid Surah and Verse number (example 114:1)")

    async def response(self, ctx, surah, verse_num) -> None:
        """
        Retrieves the correct passage from the pre-loaded json files so that the output may contain the arabic, english and transliterated text for different verses of the Quran.
        :param ctx: The context of the channel this was called from
        :param surah: The surah that is to be processed
        :param verse_num: The verse that is to be processed
        :return: None
        """
        arabic = self.quran[str(surah["id"])][verse_num]["text"]
        trans = self.transliteration[str(surah["id"])][verse_num]["text"]
        english = self.quran_en[str(surah["id"])][verse_num]["text"]
        await ctx.send(
            f"# {arabic}\n## {trans} \n\n**Meaning:** {english}\n-# {surah["transliteration"]}:{verse_num+1}")

    @commands.command()
    async def surah(self, ctx, *args):
        """
        Fetches a Surah from the Quran and returns it in full to the user.
        :param ctx: The context of the channel this was called from
        :param args: The Surah number which the user wishes to call (e.g 114)
        :return: None
        """
        if len(args) == 0 or not args[0].isdigit():
            await ctx.send("Please enter a valid number for the surah! (1 - 114)")
            return
        surah_num = args[0]
        name = self.chapters[int(surah_num)-1]["name"]
        name_trans = self.chapters[int(surah_num)-1]["transliteration"]
        msg = f"# __{name} - {name_trans}__ \n"
        for verse in self.quran[surah_num]:
            next_verse = f"## ﴾{verse["verse"]}﴿ - {verse["text"]}\n"
            if len(msg) + len(next_verse) < 2000:
                msg += next_verse
            else:
                await ctx.send(msg)
                msg = next_verse
        await ctx.send(msg)
