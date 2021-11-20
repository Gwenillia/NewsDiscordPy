import json

import discord
from discord.ext import commands

from src.config import Config
from src.database import Database
from src.defs import send_embed


class Prefix(commands.Cog):
  def __init__(self, bot):

    with open('src/config.json', 'r') as f:
      self.cfg = Config(json.loads(f.read()))

    self.bot = bot
    self.db = Database(self.bot.loop, self.cfg.postgresql_user, self.cfg.postgresql_password)

  @commands.command(name='prefix', aliases=['pre'], help="Change le prefix du bot sur le serveur",
                    usage="prefix <nouveau prefix>")
  @commands.has_permissions(administrator=True)
  async def prefix(self, ctx, new_prefix: str = None):
    if new_prefix is None:
      await ctx.send("Tu dois préciser un prefix pour que je puisse le changer :relieved:")
      return

    await self.db.execute('UPDATE guild SET prefix = $1 WHERE discord_guild_id = $2', new_prefix, ctx.message.guild.id)
    await ctx.send(f'Le prefix a bien été changé pour {new_prefix}')

  @prefix.error
  async def handle_error(self, ctx, error):
    if isinstance(error, commands.MissingPermissions):
      emb = discord.Embed(description="Tu n'as pas la permission pour faire cela :sob:", color=0xff0000)
      await send_embed(ctx, emb)

    elif isinstance(error, commands.BotMissingPermissions):
      emb = discord.Embed(description="Désolé, je n'ai pas les permissions de faire ça :sob:", color=0xff0000)
      await send_embed(ctx, emb)


def setup(bot):
  bot.add_cog(Prefix(bot))
