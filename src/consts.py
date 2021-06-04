import time

import pytz
from discord.ext import commands

CSV_PARAM = "./param.csv"
date = time.time()
titles = []
TEMP_IMG = "temp-image{}.jpg"
bot = commands.Bot(command_prefix=';', help_command=None)
DEFAULT_COLOR = 0x2b41ff
PARAM_CSV = []
FIELD_NAMES = []
TZINFOS = {
    'PDT': pytz.timezone('US/Pacific'),
    '+0200': pytz.timezone('Africa/Cairo')
}
