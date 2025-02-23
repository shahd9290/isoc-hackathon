import asyncio
import discord
from discord.ext import commands, tasks
import datetime
import aiohttp


BASE_PRAYER_TIMES_API_URL = "http://api.aladhan.com/v1/"

class PrayerTimesCog(commands.Cog, name="Prayer Times Commands"):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_loop.start()
        self.guild_settings = {}

    def cog_unload(self):
        self.reminder_loop.cancel()

    @commands.command(name="location", help="Set your location for prayer times.")
    async def set_location(self, ctx, location: str = None):
        if location is None:
            await ctx.send("Salam Alaikum! Please provide a city (e.g., London, Dubai):")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
                location = msg.content
            except asyncio.TimeoutError:
                return await ctx.send("Timeout. Please try the command again.")

        # Validate location
        prayer_times = await self.fetch_prayer_times(location)
        if not prayer_times:
            return await ctx.send("⚠️ Invalid city. Please try another location.")

        self.guild_settings[ctx.guild.id] = {
            'location': location,
            'channel_id': ctx.channel.id,
            'reminder_offset': 0  # Default no pre-reminder
        }

        await ctx.send(f"📍 Location set to **{location}**. Use `!setreminder [minutes]` for pre-reminders.")

    @commands.command(name="setreminder", help="Set a pre-reminder for each prayer.")
    async def set_reminder(self, ctx, minutes: int):
        if ctx.guild.id not in self.guild_settings:
            return await ctx.send("❌ Set location first with `!location`.")

        if minutes < 0 or minutes > 60:
            return await ctx.send("⚠️ Please enter a value between 0 and 60 minutes.")

        self.guild_settings[ctx.guild.id]['reminder_offset'] = minutes
        await ctx.send(f"⏰ Pre-reminder set to **{minutes}** minutes before each prayer.")

    @commands.command(name="pray", help="Go to pray")
    async def go_to_prayer(self, ctx, name="NoOne"):
        await ctx.send(f"{name}, it's time to pray!")

    @commands.command(name="prayertimes", help="Get prayer times for a location.")
    async def get_prayer_times(self, ctx, date_str: str = None):
        if ctx.guild.id not in self.guild_settings:
            return await ctx.send("❌ Set location first with `!location`.")

        location = self.guild_settings[ctx.guild.id]['location']
        prayer_times = await self.fetch_prayer_times(location, date_str)

        if not prayer_times:
            return await ctx.send("⚠️ Failed to fetch prayer times. Check the city/date.")

        # Format title with date if provided
        title_date = ""
        if date_str:
            try:
                date_obj = datetime.datetime.strptime(date_str, "%d-%m-%Y")
                title_date = f" on {date_obj.strftime('%d %b %Y')}"
            except ValueError:
                return await ctx.send("⚠️ Invalid date format. Use **DD-MM-YYYY**.")

        embed = discord.Embed(title=f"🕌 Prayer Times for {location}{title_date}", color=0x00ff00)
        for prayer, time in prayer_times.items():
            embed.add_field(name=prayer, value=time, inline=False)
        await ctx.send(embed=embed)

    @commands.command(
        name="hijri",
        help="Get Hijri date information.\nUsage: `!hijri [DD-MM-YYYY]`",
        brief="Show Hijri calendar information"
    )
    async def get_hijri_date(self, ctx, date_str: str = None):
        if date_str is None:
            if ctx.guild.id not in self.guild_settings:
                return await ctx.send("❌ Set location first with `!location`.")
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
                await ctx.send("⚠️ Unable to fetch Hijri date information.")
        else:
            try:
                date = datetime.datetime.strptime(date_str, "%d-%m-%Y")
                hijri_date = await self.convert_to_hijri(date)
                await ctx.send(f"The Gregorian date {date_str} corresponds to: `{hijri_date}`")
            except ValueError:
                await ctx.send("⚠️ Invalid date format. Use **DD-MM-YYYY**.")

    @commands.command(name="nextprayer", help="Get the next prayer time.")
    async def next_prayer(self, ctx):
        if ctx.guild.id not in self.guild_settings:
            return await ctx.send("❌ Set location first with `!location`.")

        location = self.guild_settings[ctx.guild.id]['location']
        prayer_times = await self.fetch_prayer_times(location)
        if not prayer_times:
            return await ctx.send("⚠️ Unable to fetch prayer times.")

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

        upcoming = {p: t for p, t in prayer_times_dt.items() if t > now}
        if upcoming:
            next_prayer, next_time = min(upcoming.items(), key=lambda item: item[1])
            delta = next_time - now
        else:
            tomorrow = today + datetime.timedelta(days=1)
            prayer_times_tomorrow = await self.fetch_prayer_times(location, tomorrow.strftime("%d-%m-%Y"))
            if not prayer_times_tomorrow:
                return await ctx.send("⚠️ Unable to fetch tomorrow's prayer times.")
            try:
                fajr_time_str = prayer_times_tomorrow.get("Fajr")
                next_time = datetime.datetime.strptime(fajr_time_str, "%H:%M")
                next_time = next_time.replace(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)
                next_prayer = "Fajr"
                delta = next_time - now
            except Exception:
                return await ctx.send("⚠️ Error determining Fajr time.")

        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        await ctx.send(f"Next prayer: **{next_prayer}** in {hours}h {minutes}m ⏳")

    async def fetch_prayer_times(self, location, date_str=None):
        url = f"{BASE_PRAYER_TIMES_API_URL}timingsByCity?city={location}&country=&method=2"
        if date_str:
            url += f"&date={date_str}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                timings = data['data']['timings']
                return {
                    "Fajr": timings['Fajr'],
                    "Sunrise": timings['Sunrise'],
                    "Dhuhr": timings['Dhuhr'],
                    "Asr": timings['Asr'],
                    "Maghrib": timings['Maghrib'],
                    "Isha": timings['Isha'],
                    "Imsak": timings['Imsak'],
                    "Midnight": timings['Midnight']
                }

    async def fetch_hijri_date_info(self, location):
        url = f"{BASE_PRAYER_TIMES_API_URL}timingsByCity?city={location}&country=&method=2"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    hijri = data['data']['date']['hijri']
                    date_en = f"{hijri['day']} {hijri['month']['en']} {hijri['year']} AH"
                    date_ar = f"{hijri['day']} {hijri['month']['ar']} {hijri['year']} هـ"
                    weekday_en = hijri.get('weekday', {}).get('en', '')
                    weekday_ar = hijri.get('weekday', {}).get('ar', '')
                    holidays = hijri.get('holidays', [])
                    return {
                        "date_en": date_en,
                        "date_ar": date_ar,
                        "weekday_en": weekday_en,
                        "weekday_ar": weekday_ar,
                        "holidays": holidays,
                    }
                else:
                    return None

    async def convert_to_hijri(self, date):
        url = f"{BASE_PRAYER_TIMES_API_URL}gToH?date={date.strftime('%d-%m-%Y')}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    hijri = data['data']['hijri']
                    return f"{hijri['day']} {hijri['month']['en']} {hijri['year']} AH"
                else:
                    return "⚠️ Conversion failed"

    @tasks.loop(minutes=1)
    async def reminder_loop(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")

        for guild_id, settings in self.guild_settings.items():
            location = settings['location']
            channel = self.bot.get_channel(settings['channel_id'])
            if not channel:
                continue

            prayer_times = await self.fetch_prayer_times(location)
            if not prayer_times:
                continue

            offset = settings.get('reminder_offset', 0)
            for prayer, time_str in prayer_times.items():
                if prayer not in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
                    continue

                try:
                    prayer_time = datetime.datetime.strptime(time_str, "%H:%M")
                    prayer_time = prayer_time.replace(year=now.year, month=now.month, day=now.day)
                    reminder_time = prayer_time - datetime.timedelta(minutes=offset)
                    if reminder_time.strftime("%H:%M") == current_time:
                        await channel.send(
                            content=f"@everyone ⏳ **{prayer}** in **{offset}** minutes!",
                            embed=discord.Embed(
                                title=f"🕌 {prayer} Time Approaching",
                                description=f"Time: {time_str}",
                                color=0x00ff00
                            )
                        )
                except Exception as e:
                    print(f"Reminder error: {e}")

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(PrayerTimesCog(bot))