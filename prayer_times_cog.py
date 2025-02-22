import discord
from discord.ext import commands, tasks
import datetime


class PrayerTimesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pray")
    async def go_to_prayer(self, ctx, name= "NoOne"):
        await ctx.send("You have to go pray rn!")



