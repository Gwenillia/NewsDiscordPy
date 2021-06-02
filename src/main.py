import asyncio
import csv
import os
import time
import urllib.request
import uuid
from datetime import datetime

import discord
import feedparser
from discord.ext import commands, tasks

date = time.time()
titles = []

token = 'NDk1NzUwMDcxNjI4MDcwOTEy.W7AVOw.pIcPHMzRQCYzVfP_Ahhu2IlcRJI'
bot = commands.Bot(command_prefix='.')


@bot.event
async def on_ready():
    feed_multi_news_rss.start()
    print('bot is running')


@tasks.loop(seconds=10)
async def feed_multi_news_rss():
    global date
    global titles
    if datetime.fromtimestamp(time.time()).day != datetime.fromtimestamp(date).day:
        print(date)
        date = time.time()
        titles = []
    with open("param.csv") as csvfile:
        reader = csv.DictReader(csvfile)

        tasks = []

        for row in reader:
            task = asyncio.create_task(feed_news_rss(row))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)


async def feed_news_rss(row):
    await asyncio.sleep(1)

    newsFeed = feedparser.parse(row["fluxrss"])
    for entry in reversed(newsFeed.entries):
        uid = uuid.uuid1()

        # parse time
        raw_article_date = entry.published

        try:
            article_detailed_date = time.strptime(raw_article_date, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            article_detailed_date = time.strptime(raw_article_date, "%a, %d %b %Y %H:%M:%S %Z")
        article_short_date = time.strftime("%d/%m/%Y à %Hh%M", article_detailed_date)

        article_timestamp = time.mktime(article_detailed_date)

        if (date > article_timestamp) and (entry.title in titles):
            pass
        elif (date < article_timestamp) and (entry.title not in titles):

            titles.append(entry.title)

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

            # set channel
            channel = bot.get_channel(int(row["channel"]))

            # set embed
            e = discord.Embed()
            e = discord.Embed(title=entry.title, url=entry.link, description=entry.summary, color=0xff0000)
            e.set_author(name=row["name"])
            e.set_footer(text=article_short_date)
            file = discord.File(temp_image, filename=temp_image)
            e.set_image(url="attachment://" + temp_image)
            await channel.send(file=file, embed=e)
            os.remove(temp_image)


bot.run(token)
