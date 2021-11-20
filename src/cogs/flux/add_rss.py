import json
import ssl
import time

import discord
import feedparser
from discord.ext import commands

import src.consts as consts
from src.config import Config
from src.consts import DEFAULT_COLOR
from src.database import Database
from src.defs import send_embed


class AddRss(commands.Cog):
  def __init__(self, bot):

    with open('src/config.json', 'r') as f:
      self.cfg = Config(json.loads(f.read()))

    self.bot = bot
    self.db = Database(self.bot.loop, self.cfg.postgresql_user, self.cfg.postgresql_password)

  @commands.command(name="addRss", aliases=["ar"], usage="addRss <nom du flux> <lien vers le flux> <#channel>",
                    help='Permet d\'ajouter un flux RSS')
  @commands.has_permissions(manage_channels=True)
  async def add_rss(self, ctx, rules_name, flux_rss, channel):

    consts.date = time.time()
    try:
      # Monkeypatching certificat
      _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
      pass
    else:
      ssl._create_default_https_context = _create_unverified_https_context
    try:
      channel_id = int(channel[2:len(channel) - 1])
    except ValueError:
      await send_embed(ctx,
                       discord.Embed(
                         description=f'Un problème est survenue avec le channel **{channel}**. :sob:',
                         color=DEFAULT_COLOR))
      return
    if len(feedparser.parse(flux_rss).entries) == 0:
      emb = discord.Embed(description=f'Ton flux rss **{flux_rss}** ne retourne rien. :sweat_smile:',
                          color=DEFAULT_COLOR)

    else:
      try:
        req = await self.db.fetch(
          'SELECT EXISTS(SELECT 1 FROM flux WHERE url = $1 AND flux_name = $2 AND discord_channel_id = $3)',
          flux_rss, rules_name, channel_id)
        res = req[0][0]
      except AttributeError:
        print('error: {0}'.format(AttributeError.args))

      if res is True:
        emb = discord.Embed(
          description=f'Le flux **{rules_name}** est déjà présent ! va voir dans **{channel}**',
          color=DEFAULT_COLOR)
        return

      else:
        try:
          await self.db.execute(
            'INSERT INTO flux (GUILD_ID, url, flux_name, discord_channel_id) SELECT ID, $1, $2, $3 FROM guild WHERE discord_guild_id = $4',
            flux_rss, rules_name, channel_id, ctx.guild.id)
        except Exception as ex:
          print('error {0}:{1!r}'.format(type(ex).__name__, ex.args))

        emb = discord.Embed(description=f'Ton flux rss **{flux_rss}** a bien été ajouté :100:',
                            color=DEFAULT_COLOR)

      await send_embed(ctx, emb)

  @add_rss.error
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
  bot.add_cog(AddRss(bot))
