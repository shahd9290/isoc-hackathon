from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.command()
    async def addNum(self, ctx, *args):
        try:
            sum = 0
            for i in args:
                sum += int(i)
            await ctx.send(sum)
        except:
            await ctx.send("Detected Strings!")