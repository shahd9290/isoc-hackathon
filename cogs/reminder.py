import os
import discord
import json
from dotenv import load_dotenv
from discord.ext import commands, tasks
import random

load_dotenv() 
TOKEN = os.getenv('DISCORD_TOKEN') 

class SunnahReminder(commands.Cog): 
    def __init__ (self,bot):
        self.bot = bot  
        self.sunnah = self.load_sunnah() 
        self.reminder.start() 

    def load_sunnah(self): 
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
            print("Sunnah not found!")
            return []

    @tasks.loop(minutes = 1)
    async def reminder(self): 
        channel = self.bot.get_channel(1342876392165212200) #channel ID
        if self.sunnah: 
            sunnah = random.choice(self.sunnah)
            await channel.send(f"{sunnah['text']} - {sunnah['source']}")

    @reminder.before_loop
    async def before_reminder(self): 
        await self.bot.wait_until_ready()

async def setup(bot): 
        await bot.add_cog(SunnahReminder(bot))
