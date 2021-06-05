from defs import *


class DelRss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="delRss", help='Permet de supprimer un flux RSS')
    async def del_rss(self, ctx, rules_name: str = None):
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


def setup(bot):
    bot.add_cog(DelRss(bot))
