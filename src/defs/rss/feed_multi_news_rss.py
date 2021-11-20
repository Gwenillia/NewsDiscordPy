import asyncio
import time
from datetime import datetime

from discord.ext import tasks

import src.consts as consts
from ..rss import load_flux, feed_news_rss


@tasks.loop(seconds=10)
async def feed_multi_news_rss(bot):
  if datetime.fromtimestamp(time.time()).day != datetime.fromtimestamp(consts.date).day:
    consts.date = time.time()
    consts.titles = []

  functions = [feed_news_rss(flux, bot) for flux in await load_flux(bot)]
  await asyncio.gather(*functions)
