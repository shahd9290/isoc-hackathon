from discord.ext import commands

class Questions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quiz(self, ctx):
        member = ctx.author
        await ctx.send("Do you want to start a quiz?")

        msg = await self.bot.wait_for("message")

        if msg.content.lower() == "yes" and msg.author == member:
            await ctx.send("Great!")
            # load question
            # loop through questions
            # wait for user input
            # if input matches answer
            # increment score
        else:
            await ctx.send("Nevermind!")
        