import os
import discord
import json
from dotenv import load_dotenv
from discord.ext import commands, tasks
import random

load_dotenv() 
TOKEN = os.getenv('DISCORD_TOKEN') 

class HadithCommands(commands.Cog): 
    def __init__ (self,bot):
        self.bot = bot  
        self.hadiths = self.load_hadiths() 
         

    def load_hadiths(self): 
        try: 
            with open('nawawi40.json', 'r', encoding='utf-8') as f: 
                data = json.load(f) 
                hadiths = data['hadiths']
                formatted_hadiths = [
                    {
                         "text": hadith['english']['text'],
                        "source": f"Narrated by {hadith['english']['narrator']}"
                    }
                    for hadith in hadiths 
                ]
                return formatted_hadiths
        except FileNotFoundError: 
            print("Hadiths not found!")
            return []

    @commands.command(name="hadith")
    async def get_hadith(self, ctx): 
       if self.hadiths: 
            hadith = random.choice(self.hadiths)
            
            embed = discord.Embed(
                title="Daily Hadith Reminder from Imam Nawawi's collection of 40 Hadith", 
                description=f"{hadith['text']}\n\n{hadith['source']}",
                color=discord.Color.blue(),
            )
            await ctx.send(embed=embed)
       else:
            await ctx.send("No Hadiths available")

            

   
async def setup(bot): 
        await bot.add_cog(HadithCommands(bot))
