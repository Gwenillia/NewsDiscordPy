import asyncio
import csv
import os
import time
import urllib.request
import uuid

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

    for entry in reversed(newsFeed.entries):

        uid = uuid.uuid1()
        
        # get picture
        picnews = entry.links[1].href
        temp_image = "temp-image" + str(uid) + ".jpg"

        req = urllib.request.Request(picnews,
                                     headers={
                                         'User-agent':
                                             'Mozilla/5.0 (Windows NT 5.1; rv:43.0) Gecko/20100101 Firefox/43.0'})

        resp = urllib.request.urlopen(req)
        with open(temp_image, "wb") as fd:
            fd.write(resp.read())

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
        file = discord.File(temp_image, filename=temp_image)
        e.set_image(url="attachment://" + temp_image)
        await channel.send(file=file, embed=e)
        os.remove(temp_image)


bot.run(token)
