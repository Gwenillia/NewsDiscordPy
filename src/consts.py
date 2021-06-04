import time

from discord.ext import commands

CSV_PARAM = "./param.csv"
date = time.time()
titles = []
TEMP_IMG = "temp-image{}.jpg"
bot = commands.Bot(command_prefix=';', help_command=None)
DEFAULT_COLOR = 0x2b41ff
PARAM_CSV = []
FIELD_NAMES = []
