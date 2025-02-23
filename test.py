from discord.ext import commands

class Test(commands.Cog):
    """Test class used to test configuration of the discord.py library"""
    def __init__(self, bot):
        """
        Initialises the class.

        :param bot: The discord bot object.
        """
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        """
        Ensures that the bot is online and is able to receive commands.

        :param ctx: The context of the channel.
        """
        await ctx.send("Pong!")

    @commands.command()
    async def addNum(self, ctx, *args):
        """
        Tests taking arguments in a function by returning the sum of all arguments

        :param ctx: The context of the channel
        :param args: A list of arguments to pass to the function
        """
        try:
            sum = 0
            for i in args:
                sum += int(i)
            await ctx.send(sum)
        except:
            await ctx.send("Detected Strings!")