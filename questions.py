from discord.ext import commands
import discord
import json

class Questions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quiz(self, ctx):
        member = ctx.author
        await ctx.send("Do you want to start a quiz?")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await self.bot.wait_for("message", check=check, timeout=30.0)

        if msg.content.lower() == "yes" and msg.author == member:
            await ctx.send("Great!")
            score = 0
            # load question
            with open("data.json", "r") as file:
                data = json.load(file)
            # loop through questions
            for questionJson in data["quiz"]:
                question = questionJson["question"]
                options = questionJson["options"]
                answer = questionJson["answer"].lower()   
                
                desc = ""
                for option in options:
                    desc += f"{options.index(option)+1}. {option}\n"
                embed = discord.Embed(title=question, colour=discord.Colour.red(), description=desc)          
                await ctx.send(embed=embed)
                # wait for user input
                ans = await self.bot.wait_for("message", check=check, timeout=30.0)
                # validation to make sure option is in options.
                if ans.content.lower() == answer:
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
        