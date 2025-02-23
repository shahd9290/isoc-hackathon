import os
import discord
import json
from dotenv import load_dotenv
from discord.ext import commands, tasks
import random

load_dotenv() 
TOKEN = os.getenv('DISCORD_TOKEN')  

class DuaReminder(commands.Cog): 
    
    def __init__(self,bot):
        self.bot = bot  
        self.dua= self.load_dua() 
        self.reminder.start()  

    def load_dua(self): 
        try: 
            with open('data/hadith_en.json', 'r', encoding='utf-8') as f:
                data = json.load(f) 
                return data
        except FileNotFoundError: 
            print("Duas not found!")
            return []

    @tasks.loop(seconds = 3600)
    async def reminder(self): 
        channel = self.bot.get_channel(1343180275831672902) #channel ID
        if self.dua: 
            dua = random.choice(self.dua)
            embed = discord.Embed(
                title=dua['title'], 
                description=f"**Arabic:**\n{dua['arabic']}\n\n**English:**\n{dua['translation']}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Source: {dua['source']}")
            embed.timestamp = discord.utils.utcnow()
            await channel.send(embed=embed)
    @reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(DuaReminder(bot))
