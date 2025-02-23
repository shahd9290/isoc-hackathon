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
            with open('data/reminders.json', 'r', encoding='utf-8') as f:
                data = json.load(f) 
                reminders = data['reminders']
                formatted_reminders = [
                    {
                        "text": reminder['text'],
                        "source": reminder['source'],
                        "title": reminder['title']
                    }
                    for reminder in reminders 
                ]
                return data['reminders']
        except FileNotFoundError: 
            print("Sunnah Reminder not found!")
            return []

    @tasks.loop(seconds = 3600 )
    async def reminder(self): 
        channel = self.bot.get_channel(1342876392165212200) #channel ID
        if self.sunnah: 
            reminder = random.choice(self.sunnah)
            
            embed = discord.Embed(
                title=reminder['title'],
                description=reminder['text'],
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Source: {reminder['source']}")
            embed.timestamp = discord.utils.utcnow() 
            await channel.send(embed=embed)

            

    @reminder.before_loop
    async def before_reminder(self): 
        await self.bot.wait_until_ready()

async def setup(bot): 
        await bot.add_cog(SunnahReminder(bot))
