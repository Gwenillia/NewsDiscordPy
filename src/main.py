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
import pandas as pd
from discord.ext import commands, tasks
from skimage import io

date = time.time()
titles = []

token = 'NDk1NzUwMDcxNjI4MDcwOTEy.W7AVOw.pIcPHMzRQCYzVfP_Ahhu2IlcRJI'
bot = commands.Bot(command_prefix='.', help_command=None)


@bot.command()
async def addRss(ctx, rules_name: str = None, flux_rss: str = None, channel: str = None):
    if (rules_name == None and flux_rss == None and channel == None):
        await ctx.send('Il manque des arguments. Commande **help**  :sweat_smile:')
        return

    try:
        channel_id = int(channel[2:len(channel) - 1])
    except ValueError:
        await ctx.send('Un problème est survenue avec le channel **{}**. :sob:'.format(channel))
        return

    if not re.fullmatch(".*[a-zA-Z0-9]", rules_name):
        await ctx.send('Tu as mis des caractères spéciaux dans le nom : **{}**. :sweat_smile:'.format(rules_name))
    elif bot.get_channel(channel_id) is None:
        await ctx.send('Tu as mis un **channel non valide**. :sweat_smile:')
    elif len(feedparser.parse(flux_rss).entries) == 0:
        await ctx.send('Ton flux rss **{}** ne retourne rien. :sweat_smile:'.format(flux_rss))
    else:
        row_contents = [flux_rss, rules_name, channel_id]

        try:
            with open("param.csv", 'a+', newline='') as write_obj:
                # Create a writer object from csv module
                csv_writer = writer(write_obj)
                # Add contents of list as last row in the csv file
                csv_writer.writerow(row_contents)

            await ctx.send('Le flux de news : **{}** a correctement été ajouté ! :100:'.format(rules_name))
        except ValueError:
            await ctx.send('Une erreur s\'est produite lors de la sauvegarde du flux rss. Désolé :sob:')


@bot.command()
async def delRss(ctx, rules_name: str = None):
    if (rules_name == None):
        await ctx.send('Il manque des arguments. Commande **help**  :sweat_smile:')
        return

    try:
        if delete_row(rules_name) == False:
            await ctx.send('Le flux de news : **{}** n\'a pu être supprimé ! :sweat_smile:'.format(rules_name))
            return
                
        await ctx.send('Le flux de news : **{}** a correctement été supprimé ! :100:'.format(rules_name))
    except ValueError:
        await ctx.send('Une erreur s\'est produite lors de la suppression du flux rss. Désolé :sob:')


@bot.command()
async def help(ctx):
    help_e = discord.Embed(description="Voici mes commandes.",
                           color=0x2b41ff)
    help_e.add_field(name="Ajout d'un flux RSS", value="addRss [nom du flux] [lien du flux] [#channel]", inline=False)
    help_e.add_field(name="Suppression d'un flux RSS", value="delRss [nom du flux]", inline=False)
    await ctx.send(embed=help_e)


@bot.command()
async def flux(ctx):
    flux_columns_names = ['fluxrss', 'name', 'channel']
    flux_datas = pd.read_csv('param.csv', names=flux_columns_names)
    flux_names = flux_datas.name.tolist()
    flux_names.pop(0)
    flux_channels = flux_datas.channel.tolist()
    flux_channels.pop(0)
    print(flux_names)

    flux_e = discord.Embed(description="Voici la liste des flux actuellement en vigueur", color=0x2b41ff)
    for i in range(0, len(flux_names)):
        flux_e.add_field(name=flux_names[i], value="<#{}>".format(flux_channels[i]), inline=False)
    await ctx.send(embed=flux_e)


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

            # delete flux if channel don't exist
            if channel is None:
                delete_row(row["name"])
                return

            # set summary
            summary = re.sub("<.*?>", "", entry.summary)

            # set embed
            e = discord.Embed(title=entry.title, url=entry.link, description=summary, color=hex_int_color)
            e.set_author(name=row["name"])
            e.set_footer(text=article_short_date)
            file = discord.File(temp_image, filename=temp_image)
            e.set_image(url="attachment://" + temp_image)
            await channel.send(file=file, embed=e)
            os.remove(temp_image)


def delete_row(rules_name):
    lines = list()
    row_length = 0
    result = False

    with open('param.csv', 'r') as read_file:
        reader = csv.reader(read_file)

        for row in reader:
            row_length += 1
            if row_length == 1:
                lines.append(row)
            else:
                if str.lower(rules_name) != str.lower(row[1]):
                    lines.append(row)

    if row_length != len(lines):
        with open('param.csv', 'w', newline='') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(lines)
            result = True

    return result


bot.run(token)
