import os

import discord
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import random
import aiohttp
import json

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
    async def zakatHelp(self,ctx):
        help_embed = discord.Embed(title="", colour= discord.Colour.purple())
        
        help_embed.add_field(name="Quick Calculation", value="use `!zakat [amount] to calculate zakat for a singular amount", inline=False)
        help_embed.add_field(name="Detailed Calculation",value="use `!zakatCalc for a more interactive and detailed calculation",inline=False)
        help_embed.add_field(name="About Nisab", value=f"Current Nisab threshold: {85 * self.gold_price:,.2f}" " (based on 85g of gold)",inline=False)
        await ctx.send(embed = help_embed)


    @commands.command()
    async def zakatCalc (self,ctx):
        try:
            embed = discord.Embed(title="Zakat Calculator", colour=discord.Colour.blue())
            embed.description = "Enter assets in following categories"
            await ctx.send(embed=embed)



            async def getAmount(prompt):
                await ctx.send(prompt)
                msg = await self.bot.wait_for('message',timeout = 5.0, check = lambda m: m.author == ctx.author)
                return float (msg.content)
            
            cash = await getAmount("enter cash savings")
            gold = await getAmount("enter gold savings")
            investment = await getAmount("enter investment")
            business = await getAmount("enter assets")

            total_wealth = cash + gold+ investment+ business
            zakat_amount = total_wealth * 0.025

            result_embed = discord.Embed(title="zakat calculation result", colour= discord.Colour.blue())
            result_embed.add_field(name="cash savings", value= f"{cash:,.2f}", inline=False)
            result_embed.add_field(name="Gold",value= f"{gold:,.2f}", inline=False)
            result_embed.add_field(name="Investments",value= f"{investment:,.2f}", inline=False)
            result_embed.add_field(name="Business Assets",value= f"{business:,.2f}", inline=False)
            result_embed.add_field(name="Total Wealth",value= f"{total_wealth:,.2f}", inline=False)
            result_embed.add_field(name="Zakat Amount (2.5%)",value= f"{zakat_amount:,.2f}", inline=False)
            await ctx.send(embed=result_embed)

        except ValueError:
            error_embed= discord.Embed(title= "❌ invalid input", description="Please enter numbers", color=discord.Colour.blurple())
            await ctx.send(embed= error_embed)
        except asyncio.TimeoutError:
            error_embed = discord.Embed(title="❌ Calculation Timeout",description="Calculation timed out due to no response",color=discord.Color.dark_magenta())
            error_embed.add_field(name="What happened?",value="You did not respond within time limit",inline=False)
            error_embed.add_field(name="What to do?",value="Please use !zakatCalc to start new calculation",inline=False)

            await ctx.send(embed= error_embed)

class Allahs99Names(commands.Cog):
    def __init__(self,bot):
        self. bot = bot
        self.api_url = "https://api.aladhan.com/v1/asmaAlHusna"
    
    async def fetch_names(self):
        try:

            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        #print("API Response", data)
                        return data
                    else:
                        #print(f"api returned status code {response.status}" )
                        return None
            
        except Exception as e:
            print(f"error in fetch_names: {str(e)}")
            return None
    
    @commands.command(name="asma", aliases = ["99names","allahnames"])
    async def divine_name(self,ctx, number: int = None):
        try:
            names_data = await self.fetch_names()
            
            if not names_data or 'data' not in names_data:
                await ctx.send("unable to grab names at this moment.")
                return
            all_names = names_data['data']

            if number:
                if not 1<= number <= 99:
                    await ctx.send("please choose a number between 1 and 99")
                    return
                selected_name = all_names[number -1]
            else:
                selected_name = random.choice(all_names)
            print(f"selected name data: {selected_name}")



            name_embed = discord.Embed(title="أسماء الله الحسنى - Names of Allah",colour= discord.Colour.dark_gold())
            name_embed.add_field(name ="Number" , value=selected_name['number'] , inline = False)
            name_embed.add_field(name="Name in arabic",value=selected_name['name'],inline=False)
            name_embed.add_field(name="Transliteration", value=selected_name['transliteration'], inline=False)
            name_embed.add_field(name="English meaning", value=selected_name['en']['meaning'], inline= False)
            await ctx.send(embed=name_embed)

        except Exception as e:
            error_embed = discord.Embed(title="Error",description=f"An error occured: {str(e)}", colour=discord.Colour.dark_red())
            error_embed.add_field(name="Unable to find names",value="Apologies",inline=False)
            await ctx.send(embed= error_embed)




    @commands.command(name="searchname", aliases=["searchasma"])
    async def search_name(self, ctx, *, search_term: str):
        try:
            names_data = await self.fetch_names()
            
            if not names_data:
                await ctx.send("Unable to fetch names at this moment.")
                return
            
            # Search through the names
            matching_names = [
                name for name in names_data['data']
                if search_term.lower() in name['transliteration'].lower() or 
                search_term.lower() in name['en']['meaning'].lower()
            ]

            if not matching_names:
                await ctx.send(f"No names found matching '{search_term}'")
                return

            search_embed = discord.Embed(
                title=f"Search Results for '{search_term}'",
                colour=discord.Colour.dark_gold()
            )

            for name in matching_names[:5]:
                search_embed.add_field(
                    name=f"{name['number']}. {name['transliteration']}",
                    value=f"Arabic: {name['name']}\nMeaning: {name['en']['meaning']}",
                    inline=False
                )

            await ctx.send(embed=search_embed)

        except Exception as e:
            await ctx.send("An error occurred while searching.")