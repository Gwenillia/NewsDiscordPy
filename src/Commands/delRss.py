import defs as func
from consts import *


@bot.command()
async def delRss(ctx, rules_name: str = None):
    if rules_name is None:
        await ctx.send('Il manque des arguments. Commande **help**  :sweat_smile:')
        return

    try:
        if not func.delete_row(rules_name):
            await ctx.send('Le flux de news : **{}** n\'a pu être supprimé ! :sweat_smile:'.format(rules_name))
            return

        await ctx.send('Le flux de news : **{}** a correctement été supprimé ! :100:'.format(rules_name))
    except ValueError:
        await ctx.send('Une erreur s\'est produite lors de la suppression du flux rss. Désolé :sob:')
