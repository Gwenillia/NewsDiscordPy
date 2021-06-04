import discord

from consts import *


@bot.command()
async def help(ctx):
    help_e = discord.Embed(description="Voici mes commandes.",
                           color=DEFAULT_COLOR)
    help_e.add_field(name="Ajout d'un flux RSS", value="addRss [nom du flux] [lien du flux] [#channel]", inline=False)
    help_e.add_field(name="Suppression d'un flux RSS", value="delRss [nom du flux]", inline=False)
    await ctx.send(embed=help_e)
