import asyncio
import csv
import re
import ssl
import urllib
import urllib.request
import uuid
from datetime import datetime

# import opencv-python-headless for cv2
import cv2
import dateutil.parser
import discord
import feedparser
import numpy as np
from discord.ext import tasks
from skimage import io

from consts import *


def run():
    @bot.event
    async def on_ready():
        load_param_csv()
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
            load_param_csv()

        functions = []

        for row in PARAM_CSV:
            function = asyncio.create_task(feed_news_rss(row))
            functions.append(function)

        await asyncio.gather(*functions)

    async def feed_news_rss(row):
        await asyncio.sleep(1)

        news_feed = feedparser.parse(row["fluxrss"])
        for entry in reversed(news_feed.entries):
            uid = uuid.uuid1()
            temp_image = TEMP_IMG.format(str(uid))

            # parse time
            article_date_str = entry.published
            article_date_pdt = dateutil.parser.parse(article_date_str, tzinfos=TZINFOS)
            article_date_utc = article_date_pdt.astimezone(pytz.utc)

            article_short_date = time.strftime("%d/%m/%Y à %Hh%M", article_date_utc.timetuple())
            article_timestamp = time.mktime(article_date_utc.timetuple())

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

    # <editor-fold desc="Defs">
    def delete_row(rules_name):
        line_deleted = None
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
        with open(CSV_PARAM, 'w', newline='') as write_file:
            # Create a writer object from csv module
            writer = csv.DictWriter(write_file, fieldnames=FIELD_NAMES)
            # Add fieldnames as header
            writer.writeheader()
            # Add contents of list as last row in the csv file
            writer.writerows(PARAM_CSV)

    # </editor-fold>

    # <editor-fold desc="Commands">
    @bot.command()
    async def reload(ctx):
        try:
            load_param_csv()
        except ValueError:
            await ctx.send('Un **problême** est survenu lors du rechargement du fichier csv. :sob:')
        await ctx.send('Le fichier csv a été **rechargé**. :100:')

    @bot.command()
    async def help(ctx):
        help_e = discord.Embed(description="Voici mes commandes.",
                               color=DEFAULT_COLOR)
        help_e.add_field(name="Ajout d'un flux RSS", value="addRss [nom du flux] [lien du flux] [#channel]",
                         inline=False)
        help_e.add_field(name="Suppression d'un flux RSS", value="delRss [nom du flux]", inline=False)
        await ctx.send(embed=help_e)

    @bot.command()
    async def flux(ctx):
        flux_e = discord.Embed(description="Voici la liste des flux actuellement en vigueur", color=DEFAULT_COLOR)
        for param in PARAM_CSV:
            flux_e.add_field(name=param["name"], value="<#{}>".format(param["channel"]), inline=False)
        await ctx.send(embed=flux_e)

    @bot.command(name="delRss")
    async def del_rss(ctx, rules_name: str = None):
        if rules_name is None:
            await ctx.send('Il manque des arguments. Commande **help**  :sweat_smile:')
            return

        try:
            if not delete_row(rules_name):
                await ctx.send('Le flux de news : **{}** n\'a pu être supprimé ! :sweat_smile:'.format(rules_name))
                return

            await ctx.send('Le flux de news : **{}** a correctement été supprimé ! :100:'.format(rules_name))
        except ValueError:
            await ctx.send('Une erreur s\'est produite lors de la suppression du flux rss. Désolé :sob:')

    @bot.command(name="addRss")
    async def add_rss(ctx, rules_name: str = None, flux_rss: str = None, channel: str = None):

        global date
        date = time.time()

        try:
            # Monkeypatching certificat
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        if rules_name is None and flux_rss is None and channel is None:
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
            row_contents = {
                "fluxrss": flux_rss,
                "name": rules_name,
                "channel": channel_id
            }

            try:
                PARAM_CSV.append(row_contents)
                write_param_csv()

                await ctx.send('Le flux de news : **{}** a correctement été ajouté ! :100:'.format(rules_name))
            except ValueError:
                PARAM_CSV.remove(row_contents)
                await ctx.send('Une erreur s\'est produite lors de la sauvegarde du flux rss. Désolé :sob:')

    # </editor-fold>

    bot.run(TOKEN)


if __name__ == '__main__':
    run()
