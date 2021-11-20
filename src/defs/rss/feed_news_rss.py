import os
import re
import time
import urllib.request
import uuid

import cv2
import dateutil.parser
import discord
import feedparser
import numpy as np
import pytz
import skimage.io as io

import src.consts as consts
from src.consts import TEMP_IMG, date, TZINFOS


async def feed_news_rss(row, bot):
  news_feed = feedparser.parse(row[2])
  for entry in reversed(news_feed.entries):
    uid = uuid.uuid1()
    temp_image = TEMP_IMG.format(str(uid))

    # parse time
    article_date_str = entry.published
    article_date_pdt = dateutil.parser.parse(article_date_str, tzinfos=TZINFOS)
    article_date_utc = article_date_pdt.astimezone(pytz.utc)

    article_short_date = time.strftime("%d/%m/%Y à %Hh%M", article_date_utc.timetuple())
    article_timestamp = time.mktime(article_date_utc.timetuple())

    if (date < article_timestamp) and (entry.title not in consts.titles):
      consts.titles.append(entry.title)

      # get picture
      exception_overclocking = re.findall(r'https://.*\.jpg', str(entry.summary))

      try:
        picnews = entry.links[1].href
      except IndexError:
        picnews = exception_overclocking[0]

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
      channel_id = row[4]
      channel = bot.get_channel(int(channel_id))
      # delete flux if channel don't exist
      if channel is None:
        await bot.db.execute('''
          DELETE FROM flux WHERE discord_channel_id = $1
        ''', channel_id)
        return

      # set summary
      summary = re.sub("<.*?>", "", entry.summary)

      # set embed
      e = discord.Embed(title=entry.title, url=entry.link, description=summary, color=hex_int_color)
      e.set_author(name=row[3])
      e.set_footer(text=article_short_date)
      file = discord.File(temp_image, filename=temp_image)
      e.set_image(url="attachment://" + temp_image)
      await channel.send(file=file, embed=e)
      os.remove(temp_image)
