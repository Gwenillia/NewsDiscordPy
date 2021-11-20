from discord.ext import tasks
import time
from datetime import datetime
from ..rss import load_flux, feed_news_rss
import asyncio
import src.consts as consts

@tasks.loop(seconds=10)
async def feed_multi_news_rss(self):
    if datetime.fromtimestamp(time.time()).day != datetime.fromtimestamp(consts.date).day:
        consts.date = time.time()
        consts.titles = []

    functions = [feed_news_rss(flux) for flux in await load_flux()]
    await asyncio.gather(*functions)