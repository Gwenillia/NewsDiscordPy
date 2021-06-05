from defs import *


class DelRss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="delRss", usage="delRss <nom du flux>", help='Permet de supprimer un flux RSS')
    async def del_rss(self, ctx, rules_name: str = None):
        if rules_name is None:
            await send_embed(ctx, discord.Embed(description='Il manque des arguments. Commande **help**  :sweat_smile:',
                                                color=DEFAULT_COLOR))
            return
        try:
            if not delete_row(rules_name):
                await send_embed(ctx, discord.Embed(
                    description=f'Le flux de news : **{rules_name}** n\'a pu être supprimé ! :sweat_smile:'))
                return
            await send_embed(ctx, discord.Embed(
                description=f'Le flux de news : **{rules_name}** a correctement été supprimé ! :100:'))
        except ValueError:
            await send_embed(ctx, discord.Embed(
                description='Une erreur s\'est produite lors de la suppression du flux rss. Désolé :sob:'))


def setup(bot):
    bot.add_cog(DelRss(bot))
