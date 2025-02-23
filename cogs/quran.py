from discord.ext import commands
import discord
import json
import random

from paginator import Paginator


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

        with open("data/quran_en.json", encoding='utf-8') as en:
            self.quran_en = json.load(en)

        with open("data/transliteration.json", encoding='utf-8') as transliteration:
            self.transliteration = json.load(transliteration)

        with open("data/chapters.json", encoding='utf-8') as chapters:
            self.chapters = json.load(chapters)

    @commands.command(help="Generate a random verse from the Quran! Usage: !randomverse")
    async def randomverse(self, ctx) -> None:
        """
        Generates a random verse of the Quran with translation and meaning.
        :param ctx: The context of the channel this was called from
        :return: None
        """
        surah = self.chapters[random.randint(0, 113)]
        verse_num = random.randint(0, surah["total_verses"]-1)
        await self.response(ctx, surah, verse_num)

    @commands.command(help="Retrieve a verse from the Quran!Usage: !quran <surah:verse>")
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
        await ctx.send(f"# {arabic}\n## {trans} \n\n**Meaning:** {english}\n-# {surah['transliteration']}:{verse_num+1}")

    @commands.command(help="Retrieve a Surah from the Quran!\nUsage: !surah <surah>")
    async def surah(self, ctx, *args):
        """
        Fetches a Surah from the Quran and returns it in full to the user.
        :param ctx: The context of the channel this was called from
        :param args: The Surah number which the user wishes to call (e.g 114)
        :return: None
        """
        surah_num = 0
        if len(args) == 0:
            await ctx.send("Please enter a valid name or number for the surah! (1 - 114)")
            return
        elif not args[0].isdigit():
            # get number from chapters.json
            for chapter in self.chapters:
                if chapter["transliteration"] == args[0]:
                    surah_num = str(chapter["id"])
                    break
            if surah_num == 0:
                await ctx.send("Invalid Input! Run !view surahs to see the correct formatting")
        else:
            surah_num = args[0]
        name = self.chapters[int(surah_num)-1]["name"]
        name_trans = self.chapters[int(surah_num)-1]["transliteration"]
        messages = []
        msg = ""
        for verse in self.quran[surah_num]:
            verse_num = verse['verse']
            arabic = verse['text']

            next_verse = f"## ﴾{verse_num}﴿ - {arabic}\n"

            if len(msg) + len(next_verse) < 2000:
                msg += next_verse
            else:
                messages.append(msg)
                msg = next_verse
        messages.append(msg)

        view = Paginator(messages, title=f"__{name} - {name_trans}__ \n")
        await ctx.send(embed = view.get_embed(), view=view)

    @commands.command(help="Get a list of all the surahs!")
    async def view(self, ctx, *args):
        if len(args) == 0:
            ctx.send("Please state what you would like to view!")
            return
        elif args[0] == "surahs":
            items_per_page = 10
            pages = ["\n".join([f"**{chapter['id']}.** {chapter['transliteration']} - {chapter['name']}" for chapter in self.chapters[i:i+items_per_page]]) for i in range(0, len(self.chapters), items_per_page)]
            view = Paginator(pages, title="List of Surahs from the Quran")
            await ctx.send(embed=view.get_embed(), view=view)
        else:
            ctx.send("Invalid!")

async def setup(bot):
    await bot.add_cog(Quran(bot))