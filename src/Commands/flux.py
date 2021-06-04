import discord
import pandas as pd

from consts import *


@bot.command()
async def flux(ctx):
    flux_columns_names = ['fluxrss', 'name', 'channel']
    flux_datas = pd.read_csv(CSV_PARAM, names=flux_columns_names)
    flux_names = flux_datas.name.tolist()
    flux_names.pop(0)
    flux_channels = flux_datas.channel.tolist()
    flux_channels.pop(0)

    flux_e = discord.Embed(description="Voici la liste des flux actuellement en vigueur", color=DEFAULT_COLOR)
    for i in range(0, len(flux_names)):
        flux_e.add_field(name=flux_names[i], value="<#{}>".format(flux_channels[i]), inline=False)
    await ctx.send(embed=flux_e)
