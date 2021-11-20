import json

import discord
from discord.ext import commands

from src.config import Config
from src.consts import DEFAULT_COLOR
from src.database import Database
from src.defs import send_embed


class DelRss(commands.Cog):
  def __init__(self, bot):
    with open('src/config.json', 'r') as f:
      self.cfg = Config(json.loads(f.read()))

    self.bot = bot
    self.db = Database(self.bot.loop, self.cfg.postgresql_user, self.cfg.postgresql_password)

  @commands.command(name="delRss", aliases=['dr'], usage="delRss <nom du flux>", help='Permet de supprimer un flux RSS')
  @commands.has_permissions(manage_channels=True)
  async def del_rss(self, ctx, rules_name: str = None):
    if rules_name is None:
      await send_embed(ctx, discord.Embed(description='Il manque des arguments. Commande **help**  :sweat_smile:',
                                          color=DEFAULT_COLOR))
    else:
      try:
        req = await self.db.fetch(
          'SELECT EXISTS(SELECT ID, $1 FROM "guild" WHERE discord_guild_id = $2)',
          rules_name,
          ctx.message.guild.id
        )
        res = req[0][0]

        if res is True:
          await self.db.execute(
            'DELETE FROM flux f USING guild g WHERE g.discord_guild_id = $1 AND f.flux_name = $2',
            ctx.message.guild.id, rules_name)

          await send_embed(ctx, discord.Embed(description=f'Le flux **{rules_name}** a bien été supprimé :100:',
                                              color=DEFAULT_COLOR))

          return

      except Exception as ex:
        print('error {0}:{1!r}'.format(type(ex).__name__, ex.args))

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
