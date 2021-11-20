import ssl
import time
from discord.ext import commands
from src.defs import send_embed
import discord
from src.consts import DEFAULT_COLOR, bot, c, db
import src.consts as consts
import re
import feedparser


class AddRss(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="addRss", aliases=["ar"], usage="addRss <nom du flux> <lien vers le flux> <#channel>",
                    help='Permet d\'ajouter un flux RSS')
  @commands.has_permissions(manage_channels=True)
  @commands.bot_has_permissions(manage_channels=True)
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
    if not re.fullmatch(".*[a-zA-Z0-9]", rules_name):
      emb = discord.Embed(
        description=f'Tu as mis des caractères spéciaux dans le nom : **{rules_name}**. :sweat_smile:',
        color=DEFAULT_COLOR)
    elif bot.get_channel(channel_id) is None:
      emb = discord.Embed(description='Tu as mis un **channel non valide**. :sweat_smile:', color=DEFAULT_COLOR)
    elif len(feedparser.parse(flux_rss).entries) == 0:
      emb = discord.Embed(description=f'Ton flux rss **{flux_rss}** ne retourne rien. :sweat_smile:',
                          color=DEFAULT_COLOR)

    else:
      # connect to db
      flux = c.execute('''
                SELECT * FROM flux WHERE url = ? AND flux_name = ? AND CHANNEL = ?
            ''', (flux_rss, rules_name, channel))

      flux_bool = flux.fetchall()

      if flux_bool:
        emb = discord.Embed(
          description=f'Le flux **{rules_name}** est déjà présent ! va voir dans **{channel}**',
          color=DEFAULT_COLOR)
        await send_embed(ctx, emb)
        return

      else:
        c.execute('''
                    REPLACE INTO flux (guild_id, url, flux_name, channel)
                    VALUES (?, ?, ?, ?)
                    ''', (ctx.message.guild.id, flux_rss, rules_name, channel))
        db.commit()
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
