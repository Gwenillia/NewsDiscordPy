from discord.ext import commands
from src.defs import send_embed
import discord
from src.consts import DEFAULT_COLOR, c, db


class DelRss(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="delRss", aliases=['dr'], usage="delRss <nom du flux>", help='Permet de supprimer un flux RSS')
  @commands.has_permissions(manage_channels=True)
  @commands.bot_has_permissions(manage_channels=True)
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

  @del_rss.error
  async def handle_error(self, ctx, error):
    if isinstance(error, commands.MissingPermissions):
      emb = discord.Embed(description="Tu n'as pas la permission pour faire cela :sob:", color=0xff0000)
      await send_embed(ctx, emb)

    elif isinstance(error, commands.MissingRequiredArgument):
      await send_embed(ctx, discord.Embed(description='Il manque des arguments. Commande **help** :sweat_smile:',
                                          color=DEFAULT_COLOR))

    elif isinstance(error, commands.BotMissingPermissions):
      emb = discord.Embed(description="Désolé, je n'ai pas les permissions de faire ça :sob:", color=0xff0000)
      await send_embed(ctx, emb)


def setup(bot):
  bot.add_cog(DelRss(bot))
