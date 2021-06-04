import asyncio
import csv
import os
import re

import urllib.request
import uuid

import cv2
import discord
import feedparser
import numpy as np
from skimage import io

from Commands import addRss, delRss, flux, help, reload
from consts import *

token = 'ODUwMjgxMjQ2ODU2OTcwMjUw.YLncHg.SlDj5xJfnbjauYt23TbXZBjdb_Y'

async def feed_news_rss(row):
    await asyncio.sleep(1)

    news_feed = feedparser.parse(row["fluxrss"])
    for entry in reversed(news_feed.entries):
        uid = uuid.uuid1()
        temp_image = TEMP_IMG.format(str(uid))
        # parse time
        raw_article_date = entry.published

        article_detailed_date = try_parsing_date(raw_article_date)

        article_short_date = time.strftime("%d/%m/%Y à %Hh%M", article_detailed_date)

        article_timestamp = time.mktime(article_detailed_date)

        if (date > article_timestamp) and (entry.title in titles):
            pass
        elif (date < article_timestamp) and (entry.title not in titles):

            titles.append(entry.title)

            # get picture
            picnews = entry.links[1].href

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


def try_parsing_date(parsed_date):
    parsed_date = parsed_date.replace('PDT', '+0700')
    for f in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
        try:
            return time.strptime(parsed_date, f)
        except ValueError:
            pass
    raise ValueError('Format de date Invalide' + parsed_date)


def delete_row(rules_name):
    line_deleted = None
    row_length = 0
    result = False

    for param in PARAM_CSV:
        if rules_name == param["name"]:
            line_deleted = param

    if line_deleted is not None:
        PARAM_CSV.remove(line_deleted)
        write_param_csv()
        result = True

    return result


def load_param_csv():
    try:
        with open(CSV_PARAM, 'r') as read_file:
            reader = csv.DictReader(read_file)
            FIELD_NAMES.clear()
            FIELD_NAMES.extend(reader.fieldnames)
            for row in reader:
                PARAM_CSV.append(row)

            print("CSV Files has been loaded correctly")
        return
    except ValueError:
        pass
    raise ValueError('Impossible de lire le fichier csv {}'.format(CSV_PARAM))

def write_param_csv():
    print(PARAM_CSV)
    with open(CSV_PARAM, 'w', newline='') as write_file:
        # Create a writer object from csv module
        writer = csv.DictWriter(write_file, fieldnames=FIELD_NAMES)
        # Add fieldnames as header
        writer.writeheader()
        # Add contents of list as last row in the csv file
        writer.writerows(PARAM_CSV)
