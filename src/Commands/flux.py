import discord
from consts import *


@bot.command()
async def flux(ctx):
    flux_e = discord.Embed(description="Voici la liste des flux actuellement en vigueur", color=DEFAULT_COLOR)
    for param in PARAM_CSV:
        flux_e.add_field(name=param["name"], value="<#{}>".format(param["channel"]), inline=False)
    await ctx.send(embed=flux_e)
