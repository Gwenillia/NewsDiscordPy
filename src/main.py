from asyncio.events import get_event_loop
import discord
from discord.ext import commands, tasks
import feedparser
import csv
from datetime import date
import asyncio

token = 'NDk1NzUwMDcxNjI4MDcwOTEy.W7AVOw.pIcPHMzRQCYzVfP_Ahhu2IlcRJI'
bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    feed_multi_news_rss.start()
    print('bot in active')

@tasks.loop(seconds=20)
async def feed_multi_news_rss():
    with open("param.csv") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            await feed_news_rss(row)


async def feed_news_rss(row):
    print(row["channel"])
    await asyncio.sleep(1)

    newsFeed = feedparser.parse(row["fluxrss"])
    lineCount = 0

    for entry in reversed(newsFeed.entries):
        lineCount=+1

        #get picture
        picnews = entry.links[1].href

        #set channel
        channel = bot.get_channel(int(row["channel"]))

        #set embed
        print("ici")

        e = discord.Embed()
        e=discord.Embed(title=entry.title, url=entry.link, description=entry.summary, color=0xff0000)
        e.set_author(name=row["name"])
        e.set_footer(text=entry.published)
        e.set_image(url=picnews)
        #await channel.send(embed=e)

bot.run(token)