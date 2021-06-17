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
        else:
            flux = c.execute('''
                SELECT * FROM flux WHERE flux_name = ? AND guild_id = ?
            ''', (rules_name, ctx.message.guild.id))
            flux_bool = flux.fetchall()

            if flux_bool:
                c.execute('''
                    DELETE FROM flux WHERE guild_id = ? AND flux_name = ?
                ''', (ctx.message.guild.id, rules_name))
                db.commit()
                await send_embed(ctx, discord.Embed(description=f'Le flux **{rules_name}** a bien été supprimé :100:',
                                                    color=DEFAULT_COLOR))
                return
            else:
                await send_embed(ctx, discord.Embed(
                    description=f"Il n'existe pas de flux **{rules_name}** sur le serveur :sob:", color=DEFAULT_COLOR))


def setup(bot):
    bot.add_cog(DelRss(bot))
