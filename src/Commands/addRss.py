import re
import ssl
from csv import writer

import feedparser

from consts import *


@bot.command()
async def addRss(ctx, rules_name: str = None, flux_rss: str = None, channel: str = None):
    try:
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
        row_contents = [flux_rss, rules_name, channel_id]

        try:
            with open(CSV_PARAM, 'a+', newline='') as write_obj:
                # Create a writer object from csv module
                csv_writer = writer(write_obj)
                # Add contents of list as last row in the csv file
                csv_writer.writerow(row_contents)

            await ctx.send('Le flux de news : **{}** a correctement été ajouté ! :100:'.format(rules_name))
        except ValueError:
            await ctx.send('Une erreur s\'est produite lors de la sauvegarde du flux rss. Désolé :sob:')
