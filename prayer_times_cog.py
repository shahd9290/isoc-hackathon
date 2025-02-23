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

    @commands.command(name="hijri")
    async def get_hijri_date(self, ctx, date_str: str = None):
        """
        If no date is provided, fetches and displays the current Hijri date for your set location
        along with details in both English and Arabic.
        If a date is provided (in DD-MM-YYYY), converts that Gregorian date to Hijri.
        """
        if date_str is None:
            if ctx.guild.id not in self.guild_settings:
                return await ctx.send("Please set your location first using the `!location` command.")
            location = self.guild_settings[ctx.guild.id]['location']
            hijri_info = await self.fetch_hijri_date_info(location)
            if hijri_info:
                embed = discord.Embed(title=f"Hijri Date Information for {location}", color=0x00ff00)

                embed.add_field(name="Hijri Date (EN)", value=hijri_info["date_en"], inline=True)
                embed.add_field(name="Hijri Date (AR)", value=hijri_info["date_ar"], inline=True)

                embed.add_field(name="\u200b", value="\u200b", inline=False)

                embed.add_field(name="Weekday (EN)", value=hijri_info["weekday_en"], inline=True)
                embed.add_field(name="Weekday (AR)", value=hijri_info["weekday_ar"], inline=True)

                if hijri_info["holidays"]:
                    embed.add_field(name="Holidays", value=", ".join(hijri_info["holidays"]), inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Unable to fetch Hijri date information.")
        else:
            # Convert given Gregorian date to Hijri (using your existing convert_to_hijri function)
            try:
                date = datetime.datetime.strptime(date_str, "%d-%m-%Y")
                hijri_date = await self.convert_to_hijri(date)
                await ctx.send(f"The Gregorian date {date_str} corresponds to the Hijri date: `{hijri_date}`")
            except ValueError:
                await ctx.send("Please provide the date in the format DD-MM-YYYY.")

    @commands.command(name="nextPrayer")
    async def next_player(self, ctx):
        if ctx.guild.id not in self.guild_settings:
            return await ctx.send("Please set your location first using the `!location` command.")

        location = self.guild_settings[ctx.guild.id]['location']
        prayer_times = await self.fetch_prayer_times(location)
        if not prayer_times:
            return await ctx.send("Unable to fetch prayer times. Please try again later.")

        now = datetime.datetime.now()
        today = now.date()

        prayer_times_dt = {}
        for prayer, time_str in prayer_times.items():
            try:
                pt = datetime.datetime.strptime(time_str, "%H:%M")
                pt = pt.replace(year=today.year, month=today.month, day=today.day)
                prayer_times_dt[prayer] = pt
            except Exception:
                continue

        # Filter to find upcoming prayers (those later than now)
        upcoming = {p: t for p, t in prayer_times_dt.items() if t > now}
        if upcoming:
            # Select the prayer with the smallest time difference
            next_prayer, next_time = min(upcoming.items(), key=lambda item: item[1])
            delta = next_time - now
        else:
            # If no prayers remain today, fetch tomorrow's prayer times and use Fajr
            tomorrow = today + datetime.timedelta(days=1)
            prayer_times_tomorrow = await self.fetch_prayer_times(location, tomorrow)
            if not prayer_times_tomorrow:
                return await ctx.send("Unable to fetch tomorrow's prayer times.")
            try:
                fajr_time_str = prayer_times_tomorrow.get("Fajr")
                next_time = datetime.datetime.strptime(fajr_time_str, "%H:%M")
                next_time = next_time.replace(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)
                next_prayer = "Fajr"
                delta = next_time - now
            except Exception:
                return await ctx.send("Error determining tomorrow's Fajr time.")

        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        await ctx.send(f"Next prayer is **{next_prayer}** in {hours} hours and {minutes} minutes.")


    async def fetch_prayer_times(self, location, date_str=None):
        url = f"{BASE_PRAYER_TIMES_API_URL}timingsByCity?city={location}&country=&method=2" + (f"&date={date_str}" if date_str else "")
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


    async def fetch_hijri_date_info(self, location):
        url = f"{BASE_PRAYER_TIMES_API_URL}timingsByCity?city={location}&country=&method=2"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    hijri = data['data']['date']['hijri']
                    # Extract both English and Arabic details
                    date_en = f"{hijri['day']} {hijri['month']['en']} {hijri['year']} AH"
                    date_ar = f"{hijri['day']} {hijri['month']['ar']} {hijri['year']} هـ"
                    weekday_en = hijri.get('weekday', {}).get('en', '')
                    weekday_ar = hijri.get('weekday', {}).get('ar', '')
                    designation_en = hijri.get('designation', {}).get('expanded', '')
                    designation_ar = hijri.get('designation', {}).get('ar', '')
                    holidays = hijri.get('holidays', [])
                    return {
                        "date_en": date_en,
                        "date_ar": date_ar,
                        "weekday_en": weekday_en,
                        "weekday_ar": weekday_ar,
                        "designation_en": designation_en,
                        "designation_ar": designation_ar,
                        "holidays": holidays,
                    }
                else:
                    return None

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
                            embed = discord.Embed(title=f"It's time for {prayer} prayer!", color=0x00ff00)
                            embed.add_field(name="Location", value=location, inline=False)
                            await channel.send(content="@everyone", embed=embed)
                            await channel.send(embed=embed)

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()

