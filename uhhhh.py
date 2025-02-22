import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class Zakat(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.gold_price = 74.73

    @commands.command()
    async def zakat(self,ctx,wealth: float):
        nisab = 85* self.gold_price

        if wealth >= nisab:
           zakat_amount = wealth * 0.025
           await ctx.send(f"your zakat amount is {zakat_amount:.2f}")
        else:
            await ctx.send("you do not meet the threshold, no worries. ")

    
    @commands.command()
    async def zakatCalc (self,ctx):
        try:
            embed = discord.Embed(title="Zakat Calculator", color=discord.colour.red())
            embed.description = "Enter assets in following categories"
            await ctx.send(embed=embed)




            async def getAmount(prompt):
                await ctx.send(prompt)
                msg = await self.bot.wait_for('message',timeout = 30.0, check = lambda m: m.author == ctx.author)
                return float (msg.content)
            
            cash = await getAmount("enter cash savings")
            gold = await getAmount("enter gold savings")
            investment = await getAmount("enter investment")
            business = await getAmount("enter assets")

            total_wealth = cash + gold+ investment+ business
            zakat_amount = total_wealth * 0.025

            result_embed = discord.Embed(title="zakat calculation result", color= discord.color.green())
            result_embed.add_field(name="cash savings")
            result_embed.add_field(name="Gold")
            result_embed.add_field(name="")
            result_embed.add_field(name="")
            result_embed.add_field(name="")
            result_embed.add_field(name="")










        except ValueError:
            ctx.send("please enter correct values.")
        except TimeoutError:
            ctx.send("calculation time out.")


