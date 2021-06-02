import asyncio
import csv
import time

import discord
import feedparser
from discord.ext import commands, tasks

token = 'NDk1NzUwMDcxNjI4MDcwOTEy.W7AVOw.pIcPHMzRQCYzVfP_Ahhu2IlcRJI'
bot = commands.Bot(command_prefix='.')


@bot.event
async def on_ready():
    feed_multi_news_rss.start()
    print('bot in active')


@tasks.loop(seconds=5)
async def feed_multi_news_rss():
    with open("param.csv") as csvfile:
        reader = csv.DictReader(csvfile)

        tasks = []

        for row in reader:
            task = asyncio.create_task(feed_news_rss(row))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)


async def feed_news_rss(row):
    print(row["channel"])
    await asyncio.sleep(1)

    newsFeed = feedparser.parse(row["fluxrss"])
    lineCount = 0

    for entry in reversed(newsFeed.entries):
        lineCount = +1

        # get picture
        picnews = entry.links[1].href

        # parse time
        temp_time = entry.published
        try:
            start_time = time.strptime(temp_time, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            start_time = time.strptime(temp_time, "%a, %d %b %Y %H:%M:%S %Z")
        final_time = time.strftime("%d/%m/%Y à %Hh%M", start_time)

        # set channel
        channel = bot.get_channel(int(row["channel"]))

        # set embed
        print("ici")

        e = discord.Embed()
        e = discord.Embed(title=entry.title, url=entry.link, description=entry.summary, color=0xff0000)
        e.set_author(name=row["name"])
        e.set_footer(text=final_time)
        e.set_image(url=picnews)
        await channel.send(embed=e)


bot.run(token)
