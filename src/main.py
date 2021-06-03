import asyncio
import csv
import os
import re
import time
import urllib.request
import uuid
from csv import writer
from datetime import datetime

import cv2
import discord
import feedparser
import numpy as np
from discord.ext import commands, tasks
from skimage import io

date = time.time()
titles = []

token = 'NDk1NzUwMDcxNjI4MDcwOTEy.W7AVOw.pIcPHMzRQCYzVfP_Ahhu2IlcRJI'
bot = commands.Bot(command_prefix='.')


@bot.command()
async def add_rss(ctx, *args):
    if len(args) != 3:
        await ctx.send(
            'Tu as mis **{} argument(s)** au lieu des **3 arguments** demandés. :sweat_smile: '.format(len(args)))
    elif not re.fullmatch(".*[a-zA-Z0-9]", args[0]):
        await ctx.send('Tu as mis des caractères spéciaux dans le nom : **{}**. :sweat_smile: '.format(args[0]))
    elif not re.fullmatch(".*[0-9]", args[2]) and bot.get_channel(args[2]) is None:
        await ctx.send('Copies l\'identifiant du channel ou tu veux mettre la news. :sweat_smile: ')
    elif len(feedparser.parse(args[1]).entries) == 0:
        await ctx.send('Ton flux rss **{}** ne retourne rien. :sweat_smile:'.format(args[1]))
    else:
        row_contents = [args[1], args[0], args[2]]

        with open("param.csv", 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(row_contents)

        await ctx.send('Le flux de news : **{}** a correctement été ajouté ! :100: '.format(args[0]))


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="les actualités"))
    feed_multi_news_rss.start()
    print('bot is running')


@tasks.loop(seconds=10)
async def feed_multi_news_rss():
    global date
    global titles
    if datetime.fromtimestamp(time.time()).day != datetime.fromtimestamp(date).day:
        date = time.time()
        titles = []
    with open("param.csv") as csvfile:
        reader = csv.DictReader(csvfile)

        functions = []

        for row in reader:
            function = asyncio.create_task(feed_news_rss(row))
            functions.append(function)

        responses = await asyncio.gather(*functions)


async def feed_news_rss(row):
    await asyncio.sleep(1)

    news_feed = feedparser.parse(row["fluxrss"])
    for entry in reversed(news_feed.entries):
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

            # get dominant color
            img = io.imread(temp_image)

            pixels = np.float32(img.reshape(-1, 3))

            n_colors = 5
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
            flags = cv2.KMEANS_RANDOM_CENTERS

            _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
            _, counts = np.unique(labels, return_counts=True)
            dominant = palette[np.argmax(counts)]

            hex_string_color = '0x%02x%02x%02x' % (int(dominant[0]), int(dominant[1]), int(dominant[2]))
            hex_int_color = int(hex_string_color, 16)

            # get channel
            channel = bot.get_channel(int(row["channel"]))

            # set embed
            e = discord.Embed(title=entry.title, url=entry.link, description=entry.summary, color=hex_int_color)
            e.set_author(name=row["name"])
            e.set_footer(text=article_short_date)
            file = discord.File(temp_image, filename=temp_image)
            e.set_image(url="attachment://" + temp_image)
            await channel.send(file=file, embed=e)
            os.remove(temp_image)


bot.run(token)
