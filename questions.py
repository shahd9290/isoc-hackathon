from discord.ext import commands
import discord
import json

class Questions(commands.Cog):
    """
    This component is used to generate and run an interactive Islamic quiz, used to test the user's knowledge on a selection of Islamic topics.
    Topics are currently limited however there is always room to expand in the future.
    """
    def __init__(self, bot):
        """
        Initialises the Questions component
        :param bot: The bot object used to send commands
        """
        self.bot = bot

    @commands.command()
    async def quiz(self, ctx) -> None:
        """
        The quiz command, used to generate and run the interactive Islamic quiz.
        :param ctx: The context of the channel this was called from
        :return: None
        """
        member = ctx.author
        await ctx.send("Do you want to start a quiz?")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await self.bot.wait_for("message", check=check, timeout=30.0)

        if msg.content.lower() == "yes" and msg.author == member:
            await ctx.send("Great!")
            score = 0
            # load question
            with open("data/data.json", "r") as file:
                data = json.load(file)
            # loop through questions
            for questionJson in data["quiz"]:
                question = questionJson["question"]
                options = questionJson["options"]
                desc = ""
                for i in range(len(options)):
                    desc += f"{i+1}. {options[i]}\n"
                    options[i] = options[i].lower()
                embed = discord.Embed(title=question, colour=discord.Colour.purple(), description=desc)
                answer = questionJson["answer"].lower()
                ans_index = options.index(answer) + 1
                await ctx.send(embed=embed)

                # validation to make sure option is in options.
                while True:
                # wait for user input
                    ans = await self.bot.wait_for("message", check=check, timeout=30.0)
                    if ans.content.lower() in options or ans.content in ["1", "2", "3", "4"]:
                        break
                    else:
                        await ctx.send("Invalid Option! Please enter the answer or corresponding number.")

                # check if answer matches answer string or index + 1
                if ans.content.lower() == answer or ans.content == str(ans_index):
                    await ctx.send("Correct!")
                    score += 1
                else:
                    await ctx.send("Incorrect!")
            finalScore = discord.Embed(title="Final Score", colour = discord.Colour.green(), description=f"{score}/10")
            await ctx.send(embed=finalScore)
            # if input matches answer
            # increment score
        else:
            await ctx.send("Nevermind!")
        