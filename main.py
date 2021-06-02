import discord
from discord.ext import commands, tasks
import feedparser
import csv
from datetime import date
import time

token = 'NDk1NzUwMDcxNjI4MDcwOTEy.W7AVOw.pIcPHMzRQCYzVfP_Ahhu2IlcRJI'
bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    feed_multi_news_rss()
    print('bot in active')


def feed_multi_news_rss():
    feed_news_rss.start()

@tasks.loop(seconds=2)
async def feed_news_rss():
    listCsv = list()

    with open("param.csv") as csvfile:
        #listCsv = list(csv.reader(csvfile))
        reader = csv.DictReader(csvfile)

        print(reader)
        for row in reader:
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
                await channel.send(embed=e)

    print(listCsv)
    print(listCsv[1][0])
    # r = csv.reader(open("param.csv")) # Here your csv file
    # lines = list(r)
    # print(lines[1][1])
    # #lines[3][lineCount] = entry.published
    # writer = csv.writer(open("param.csv", "w"))
    # print(lines)
    # writer.writerows(lines)

bot.run(token)