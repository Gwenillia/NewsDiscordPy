import defs as func
from consts import *


@bot.command()
async def reload(ctx):
    try:
        func.load_param_csv()
    except ValueError:
        await ctx.send('Un **problême** est survenu lors du rechargement du fichier csv. :sob:')
    await ctx.send('Le fichier csv a été **rechargé**. :100:')
