import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import asyncio 

load_dotenv() 
TOKEN = os.getenv('DISCORD_TOKEN') 

class SunnahReminder(commands.Cog): 
    def __init__ (self,bot):
        self.bot = bot  
        self.sunnah = load_sunnah 


    def load_sunnahs(self): 
        try: 
            with open('sunnah.json', 'r',) as f: 
                data = json.load(f) 
                return data['sunnahs']
        except FileNotFoundError: 
            print("Sunnahs not found!")
            return []


