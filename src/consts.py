import os
import sqlite3
import time

import pytz
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

db = sqlite3.connect("arca_news.sqlite")
c = db.cursor()

COGS = [
    'cogs.help',
    'cogs.ping',
    'cogs.flux.add_rss',
    'cogs.flux.del_rss',
    'cogs.flux.flux',
    'cogs.flux.reload',
    'cogs.check_price',
    'cogs.prefix'
]

date = time.time()
titles = []
TEMP_IMG = "temp-image{}.jpg"


async def get_prefix(bot, message):
    req = c.execute('''
            SELECT prefix FROM guild WHERE guild_id = ?
        ''', (message.guild.id,))
    prefix = req.fetchone()[0]
    if prefix is None:  # TODO: set default prefix
        c.execute('''
            UPDATE guild SET prefix = ";" WHERE guild_id = ?
        ''', (message.guild.id,))

    return prefix


bot = commands.Bot(command_prefix=get_prefix, help_command=None, case_insensitive=True)

DEFAULT_COLOR = 0x2b41ff
FIELD_NAMES = []
TZINFOS = {
    'PDT': pytz.timezone('US/Pacific'),
    '+0200': pytz.timezone('Africa/Cairo')
}
TOKEN = os.getenv("DISCORD_TOKEN")
