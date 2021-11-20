import json

import discord
from discord.ext import commands

from src.config import Config
from src.consts import DEFAULT_COLOR
from src.database import Database
from src.defs import send_embed


class Flux(commands.Cog):

  def __init__(self, bot):
    with open('src/config.json', 'r') as f:
      self.cfg = Config(json.loads(f.read()))

    self.bot = bot
    self.db = Database(self.bot.loop, self.cfg.postgresql_user, self.cfg.postgresql_password)

  @commands.command(name="flux", help="Affiche la liste des flux et leur channels", usage="flux")
  async def flux(self, ctx):
    fluxs = await self.db.fetch(
      'SELECT f.flux_name, f.discord_channel_id FROM flux f JOIN guild g ON f.GUILD_ID = g.ID AND g.discord_guild_id = $1',
      ctx.guild.id)

    emb = discord.Embed(title="Voici la liste des flux actuellement en vigueur", color=DEFAULT_COLOR)

    for flux in fluxs:
      emb.add_field(name=flux[0], value='<#{}>'.format(flux[1]), inline=False)

    await send_embed(ctx, emb)


def setup(bot):
  bot.add_cog(Flux(bot))
