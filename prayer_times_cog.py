import asyncio
import discord
from discord.ext import commands, tasks
import datetime
import aiohttp

CHANNEL_ID = 1342837274991136808
BASE_PRAYER_TIMES_API_URL = "http://api.aladhan.com/v1/"



class PrayerTimesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_loop.start()
        self.guild_settings = {}

    def cog_unload(self):
        self.reminder_loop.cancel()

    @commands.command(name="location")
    async def set_location(self, ctx, location: str = None):

        if location is None:
            await ctx.send("Salam Alaikum, Can you provide a city? (e.g., London, New York, Dubai)")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("Sorry, took too long to respond. Please try the command again.")

            location = msg.content

        self.guild_settings[ctx.guild.id] = {
            'location': location,
            'channel_id': ctx.channel.id,
        }

        await ctx.send(f"Great! I've set your location to **{location}** and will use it to fetch prayer times.")

    @commands.command(name="pray")
    async def go_to_prayer(self, ctx, name="NoOne"):
        await ctx.send(f"{name}, it's time to pray!")

    @commands.command(name="prayerTimes")
    async def get_prayer_times(self, ctx):
        if ctx.guild.id not in self.guild_settings:
            return await ctx.send("Please set your location first using the `!location` command.")

        location = self.guild_settings[ctx.guild.id]['location']
        prayer_times = await self.fetch_prayer_times(location)

        if prayer_times:
            embed = discord.Embed(title=f"Prayer Times for {location}", color=0x00ff00)
            for prayer, time in prayer_times.items():
                embed.add_field(name=prayer, value=time, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Unable to fetch prayer times. Please try again later.")

    async def fetch_prayer_times(self, location):
        url = f"{BASE_PRAYER_TIMES_API_URL}timingsByCity?city={location}&country=&method=2"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    timings = data['data']['timings']
                    return {
                        "Fajr": timings['Fajr'],
                        "Dhuhr": timings['Dhuhr'],
                        "Asr": timings['Asr'],
                        "Maghrib": timings['Maghrib'],
                        "Isha": timings['Isha']
                    }
                else:
                    return None

    @commands.command(name="hijri")
    async def get_hijri_date(self, ctx, date_str: str = None):
        # Date of today and current location
        if date_str is None:
            if ctx.guild.id not in self.guild_settings:
                return await ctx.send("Please set your location first using the `!location` command.")

            location = self.guild_settings[ctx.guild.id]['location']
            # Get current Hijri date
            hijri_date = await self.fetch_hijri_date(location)
            await ctx.send(f"The current Hijri date in {location} is: `{hijri_date}`")
        else:
            # Convert given Gregorian date to Hijri
            try:
                date = datetime.datetime.strptime(date_str, "%d-%m-%Y")
                hijri_date = await self.convert_to_hijri(date)
                await ctx.send(f"The Gregorian date {date_str} corresponds to the Hijri date: `{hijri_date}`")
            except ValueError:
                await ctx.send("Please provide the date in the format DD-MM-YYYY.")


    async def fetch_hijri_date(self, location):
        url = f"{BASE_PRAYER_TIMES_API_URL}timingsByCity?city={location}&country=&method=2"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    hijri = data['data']['date']['hijri']
                    return f"{hijri['day']} {hijri['month']['en']} {hijri['year']} AH"
                else:
                    return "Unable to fetch Hijri date"

    async def convert_to_hijri(self, date):
        url = f"{BASE_PRAYER_TIMES_API_URL}gToH?date={date.strftime('%d-%m-%Y')}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    hijri = data['data']['hijri']
                    return f"{hijri['day']} {hijri['month']['en']} {hijri['year']} AH"
                else:
                    return "Unable to convert date"

    @tasks.loop(minutes=1)
    async def reminder_loop(self):
        now = datetime.datetime.now().strftime("%H:%M")
        print(now)
        for guild_id, settings in self.guild_settings.items():
            location = settings['location']
            channel_id = settings['channel_id']
            prayer_times = await self.fetch_prayer_times(location)

            if prayer_times:
                for prayer, time in prayer_times.items():
                    if time == now:
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            await channel.send(f"It's time for {prayer} prayer!")

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()

